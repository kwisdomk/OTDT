"""
LSTM Failure Prediction API — Track B, Step 4.

POST /predict/failure             → predict failure probability for given sensor state
GET  /predict/failure/{asset_id} → predict using latest cached sensor state for asset
GET  /predict/model/info         → current model source and Watson ML status

Priority chain (teammate-approved strategy):
  1. Watson ML REST endpoint  (if WATSON_ML_URL env var is set + reachable)
  2. Tracker 720×8 LSTM + Platt calibration (if sensor_sequence provided and artifacts present)
  3. Local .h5 model file     (ml/lstm/models/lstm_failure.h5)
  4. Synthetic fallback        (deterministic score, unblocks dev while training runs)

⚠️  SYNTHETIC DATA: Predictions are computer-generated until Step 4 (LSTM training) completes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import os
import math
import pickle
import httpx

router = APIRouter()

# ── Config ─────────────────────────────────────────────────────────────────
_WATSON_ML_URL        = os.getenv("WATSON_ML_URL", "")        # e.g. https://us-south.ml.cloud.ibm.com/...
_WATSON_ML_API_KEY    = os.getenv("WATSON_ML_API_KEY", "")
_WATSON_IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

_LOCAL_H5_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml", "lstm", "models", "lstm_failure.h5"
)

# ── Model loader (legacy .h5) ──────────────────────────────────────────────
_LSTM_MODEL    = None
_MODEL_SOURCE  = "synthetic"

try:
    if os.path.exists(_LOCAL_H5_PATH):
        import tensorflow as tf  # type: ignore
        import numpy as np       # type: ignore
        _LSTM_MODEL = tf.keras.models.load_model(_LOCAL_H5_PATH)
        _MODEL_SOURCE = "local_h5"
        print(f"[LSTM] Loaded local model from {_LOCAL_H5_PATH}")
    else:
        print("[LSTM] No local .h5 found — will try Watson ML or synthetic fallback")
except Exception as _e:
    print(f"[LSTM] Local model load failed ({_e}) — Watson ML / synthetic fallback active")


# ── Tracker 720×8 LSTM + Platt calibration loader ──────────────────────────
_TRACKER_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml", "lstm", "models", "tracker_720x8"
)
_TRACKER_MODEL_PATH  = os.path.join(_TRACKER_DIR, "lstm_tracker_720x8.keras")
_TRACKER_SCALER_PATH = os.path.join(_TRACKER_DIR, "lstm_tracker_720x8_scaler_fitted.pkl")
_TRACKER_CALIB_PATH  = os.path.join(_TRACKER_DIR, "lstm_tracker_720x8_calibration.json")

_TRACKER_MODEL = None
_TRACKER_SCALER = None
_TRACKER_CALIBRATION = None  # dict with "coefficient" and "intercept"

try:
    if os.path.exists(_TRACKER_MODEL_PATH):
        # Re-use TF if already imported above, otherwise import now
        if "tf" not in dir():
            import tensorflow as tf  # type: ignore
        if "np" not in dir():
            import numpy as np       # type: ignore
        _tracker_model_candidate = tf.keras.models.load_model(
            _TRACKER_MODEL_PATH, compile=False
        )
        # Validate input shape
        if _tracker_model_candidate.input_shape == (None, 720, 8):
            _TRACKER_MODEL = _tracker_model_candidate
            print(f"[TRACKER] Loaded 720×8 model from {_TRACKER_MODEL_PATH}")
        else:
            print(
                f"[TRACKER] Model shape mismatch: expected (None, 720, 8), "
                f"got {_tracker_model_candidate.input_shape} — skipping"
            )
    else:
        print(f"[TRACKER] No .keras model found at {_TRACKER_MODEL_PATH}")
except Exception as _te:
    print(f"[TRACKER] Model load failed ({_te})")

try:
    if os.path.exists(_TRACKER_SCALER_PATH):
        with open(_TRACKER_SCALER_PATH, "rb") as _sf:
            _tracker_scaler_candidate = pickle.load(_sf)
        if hasattr(_tracker_scaler_candidate, "n_features_in_") and _tracker_scaler_candidate.n_features_in_ == 8:
            _TRACKER_SCALER = _tracker_scaler_candidate
            print(f"[TRACKER] Loaded fitted scaler (n_features=8)")
        else:
            n = getattr(_tracker_scaler_candidate, "n_features_in_", "?")
            print(f"[TRACKER] Scaler n_features_in_={n}, expected 8 — skipping")
    else:
        print(f"[TRACKER] No scaler found at {_TRACKER_SCALER_PATH}")
except Exception as _te:
    print(f"[TRACKER] Scaler load failed ({_te})")

try:
    if os.path.exists(_TRACKER_CALIB_PATH):
        with open(_TRACKER_CALIB_PATH, "r") as _cf:
            _calib_data = json.load(_cf)
        _c = _calib_data.get("coefficient")
        _i = _calib_data.get("intercept")
        if isinstance(_c, (int, float)) and isinstance(_i, (int, float)):
            _TRACKER_CALIBRATION = {"coefficient": float(_c), "intercept": float(_i)}
            print(f"[TRACKER] Loaded Platt calibration (coeff={_c:.4f}, intercept={_i:.4f})")
        else:
            print(f"[TRACKER] Calibration JSON missing coefficient/intercept — skipping")
    else:
        print(f"[TRACKER] No calibration JSON at {_TRACKER_CALIB_PATH}")
except Exception as _te:
    print(f"[TRACKER] Calibration load failed ({_te})")


def _tracker_artifacts_available() -> bool:
    """True when all three tracker-LSTM artifacts loaded successfully."""
    return (
        _TRACKER_MODEL is not None
        and _TRACKER_SCALER is not None
        and _TRACKER_CALIBRATION is not None
    )


def _platt_sigmoid(raw_score: float, coefficient: float, intercept: float) -> float:
    """Apply Platt calibration: sigmoid(coefficient * raw_score + intercept).

    Matches the equation approved under OTD-019.
    """
    x = coefficient * raw_score + intercept
    return 1.0 / (1.0 + math.exp(-x))


# ── Watson ML token helper ─────────────────────────────────────────────────

async def _get_iam_token() -> Optional[str]:
    """Exchange API key for a short-lived IBM IAM bearer token."""
    if not _WATSON_ML_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                _WATSON_IAM_TOKEN_URL,
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": _WATSON_ML_API_KEY,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            return resp.json().get("access_token")
    except Exception as e:
        print(f"[LSTM] IAM token fetch failed: {e}")
        return None


async def _predict_watson(sensor_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Call the Watson ML REST endpoint.
    Returns a result dict or None if unavailable.
    """
    if not _WATSON_ML_URL:
        return None

    token = await _get_iam_token()
    if not token:
        return None

    try:
        payload = {
            "input_data": [{
                "fields": ["bearing_temp_c", "bearing_vibration_mms", "steam_inlet_pressure_bar"],
                "values": [[
                    sensor_state.get("bearing_temp_c", 85.0),
                    sensor_state.get("bearing_vibration_mms", 4.2),
                    sensor_state.get("steam_inlet_pressure_bar", 24.0),
                ]]
            }]
        }
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                _WATSON_ML_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            # Watson ML returns: {"predictions": [{"fields": [...], "values": [[prob]]}]}
            prob = float(data["predictions"][0]["values"][0][0])
            return _build_result(prob, sensor_state, source="watson_ml")
    except Exception as e:
        print(f"[LSTM] Watson ML call failed: {e} — falling back")
        return None


def _predict_local(sensor_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Run inference on the local .h5 model."""
    if _LSTM_MODEL is None:
        return None
    try:
        import numpy as np  # type: ignore
        # Normalise inputs (same scaler used during training — update if scaler is persisted)
        temp  = sensor_state.get("bearing_temp_c", 85.0) / 150.0
        vib   = sensor_state.get("bearing_vibration_mms", 4.2) / 10.0
        pres  = sensor_state.get("steam_inlet_pressure_bar", 24.0) / 85.0
        # Shape: (1, 1, 3) — batch=1, timestep=1, features=3
        x = np.array([[[temp, vib, pres]]], dtype="float32")
        prob = float(_LSTM_MODEL.predict(x, verbose=0)[0][0])
        return _build_result(prob, sensor_state, source="local_h5")
    except Exception as e:
        print(f"[LSTM] Local inference failed: {e}")
        return None


# ── Tracker 720×8 LSTM inference ───────────────────────────────────────────

def _predict_tracker_lstm(
    sensor_sequence: Optional[List[List[float]]],
) -> Dict[str, Any]:
    """Run inference on the tracker-aligned 720×8 LSTM with Platt calibration.

    Returns a tagged dict indicating the outcome:
        {"status": "success", "result": <prediction dict>}
        {"status": "no_sequence"}                        — no sequence provided
        {"status": "invalid_shape", "detail": <str>}     — wrong dimensions
        {"status": "missing_artifacts", "detail": <str>}  — model/scaler/calibration unavailable
        {"status": "inference_error", "detail": <str>}    — runtime failure during predict
    """
    # 1. Check sequence is provided
    if sensor_sequence is None:
        return {"status": "no_sequence"}

    # 2. Validate shape: must be list of 720 inner lists, each with 8 floats
    if not isinstance(sensor_sequence, list) or len(sensor_sequence) != 720:
        return {
            "status": "invalid_shape",
            "detail": (
                f"sensor_sequence must be a list of 720 rows, "
                f"got {len(sensor_sequence) if isinstance(sensor_sequence, list) else type(sensor_sequence).__name__}"
            ),
        }
    for i, row in enumerate(sensor_sequence):
        if not isinstance(row, list) or len(row) != 8:
            row_len = len(row) if isinstance(row, list) else type(row).__name__
            return {
                "status": "invalid_shape",
                "detail": f"Row {i} must have 8 features, got {row_len}",
            }

    # 3. Check artifacts
    missing = []
    if _TRACKER_MODEL is None:
        missing.append("model (.keras)")
    if _TRACKER_SCALER is None:
        missing.append("scaler (.pkl)")
    if _TRACKER_CALIBRATION is None:
        missing.append("calibration (.json)")
    if missing:
        return {
            "status": "missing_artifacts",
            "detail": f"Tracker LSTM artifacts not available: {', '.join(missing)}",
        }

    # 4. Inference
    try:
        import numpy as np  # type: ignore

        arr = np.array(sensor_sequence, dtype=np.float64)  # (720, 8)
        arr_scaled = _TRACKER_SCALER.transform(arr)        # (720, 8)
        x = arr_scaled.reshape(1, 720, 8).astype(np.float32)
        raw_score = float(_TRACKER_MODEL.predict(x, verbose=0)[0][0])

        # 5. Platt calibration (OTD-019)
        coeff = _TRACKER_CALIBRATION["coefficient"]
        intercept = _TRACKER_CALIBRATION["intercept"]
        calibrated = _platt_sigmoid(raw_score, coeff, intercept)

        # 6. Build result with calibrated probability as the primary value
        result = _build_result(calibrated, {}, source="local_tracker_720x8_platt")
        result["calibration_applied"] = True
        result["raw_score"] = round(raw_score, 6)
        result["calibrated_score"] = round(calibrated, 6)
        result["is_synthetic"] = False
        return {"status": "success", "result": result}

    except Exception as e:
        print(f"[TRACKER] Inference failed: {e}")
        return {
            "status": "inference_error",
            "detail": f"Tracker LSTM inference failed: {e}",
        }


def _predict_synthetic(sensor_state: Dict[str, Any], asset_id: str = "") -> Dict[str, Any]:
    """
    Deterministic synthetic prediction for demo / development.

    GDC-WP-007 is the hero asset: returns 0.34 (baseline demo: 34% 30-day
    failure probability).  Other assets scale smoothly with bearing_temp_c
    and vibration.
    """
    # Demo override for the hero asset
    if asset_id in ("GDC-WP-007", "WP-007"):
        prob = 0.34
    else:
        temp = sensor_state.get("bearing_temp_c", 85.0)
        vib  = sensor_state.get("bearing_vibration_mms", 4.2)
        # Normalised score; clamp to [0.05, 0.95]
        raw = (temp / 150.0) * 0.6 + (vib / 10.0) * 0.4
        prob = max(0.05, min(0.95, raw))
    return _build_result(prob, sensor_state, source="synthetic")


def _build_result(prob: float, sensor_state: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Common result schema for all three model sources."""
    now = datetime.now()
    # Days to failure P50: calibrated inverse of probability curve
    days_p50 = max(1, int(45 * (1.0 - prob)))
    days_p95 = max(1, int(days_p50 * 0.4))

    if prob >= 0.25:
        action = "URGENT"
    elif prob >= 0.10:
        action = "SCHEDULE_MAINTENANCE"
    else:
        action = "MONITOR"

    return {
        "failure_probability":   round(prob, 4),
        "days_to_failure_p50":   days_p50,
        "days_to_failure_p95":   days_p95,
        "recommended_action":    action,
        "optimal_maintenance_day": (now + timedelta(days=days_p50)).strftime("%Y-%m-%d"),
        "model_source":          source,
        "auc_roc":               None,  # No validated model metadata loaded; do not hardcode
        "timestamp":             now.isoformat(),
        "synthetic":             source == "synthetic",
        "disclaimer": (
            "⚠️ SYNTHETIC DATA — LSTM model not yet trained. "
            "Predictions are deterministic simulations for integration purposes only."
            if source == "synthetic"
            else "LSTM failure prediction. Model validation pending."
        ),
    }


# ── Pydantic schemas ───────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    asset_id: str = Field(..., description="Asset identifier, e.g. GDC-WP-007")
    sensor_state: Dict[str, Any] = Field(
        ...,
        description="Current sensor readings",
        examples=[{
            "bearing_temp_c": 92.5,
            "bearing_vibration_mms": 5.8,
            "steam_inlet_pressure_bar": 26.3,
        }],
    )
    force_source: Optional[str] = Field(
        default=None,
        description=(
            "Override inference priority: "
            "'watson_ml' | 'tracker_lstm' | 'local_h5' | 'synthetic'"
        ),
    )
    sensor_sequence: Optional[List[List[float]]] = Field(
        default=None,
        description=(
            "720×8 sensor time-series for tracker LSTM inference. "
            "Each inner list is one hourly reading with 8 features: "
            "temperature_c, pressure_bar, vibration_mm_s, flow_rate_kg_s, "
            "rotation_rpm, health_score, rolling_7d_temp_mean, rate_of_change_vibration."
        ),
    )


# ── Routes ─────────────────────────────────────────────────────────────────

@router.post(
    "/predict/failure",
    summary="LSTM failure probability for given sensor state",
)
async def predict_failure(request: PredictRequest):
    """
    Predicts failure probability using the LSTM model.

    **Inference priority (unless overridden by `force_source`):**
    1. Watson ML REST endpoint (if `WATSON_ML_URL` env var is set)
    2. Tracker 720×8 LSTM + Platt calibration (if `sensor_sequence` provided)
    3. Local `.h5` model (if present at `ml/lstm/models/lstm_failure.h5`)
    4. Synthetic fallback (always available)

    This matches the teammate-approved demo-resilience strategy — conference
    Wi-Fi drops won't crash the demo.
    """
    force = request.force_source

    # --- Watson ML ---
    if force in (None, "watson_ml"):
        result = await _predict_watson(request.sensor_state)
        if result:
            return result

    # --- Tracker 720×8 LSTM (OTD-016 / OTD-019) ---
    if force in (None, "tracker_lstm"):
        tracker_out = _predict_tracker_lstm(request.sensor_sequence)

        if tracker_out["status"] == "success":
            return tracker_out["result"]

        # Explicit tracker_lstm request — fail loudly with the correct code
        if force == "tracker_lstm":
            if tracker_out["status"] == "no_sequence":
                raise HTTPException(
                    status_code=422,
                    detail="sensor_sequence (720×8) is required for tracker_lstm source",
                )
            if tracker_out["status"] == "invalid_shape":
                raise HTTPException(
                    status_code=422,
                    detail=tracker_out["detail"],
                )
            if tracker_out["status"] == "missing_artifacts":
                raise HTTPException(
                    status_code=503,
                    detail=tracker_out["detail"],
                )
            # inference_error
            raise HTTPException(
                status_code=503,
                detail=tracker_out.get("detail", "Tracker LSTM inference failed"),
            )

        # Implicit attempt — fall through silently to next source

    # --- Local .h5 ---
    if force in (None, "local_h5"):
        result = _predict_local(request.sensor_state)
        if result:
            return result

    # --- Synthetic fallback ---
    return _predict_synthetic(request.sensor_state, asset_id=request.asset_id)


@router.get(
    "/predict/failure/{asset_id}",
    summary="LSTM failure probability using demo sensor state for asset",
)
async def predict_failure_by_asset(asset_id: str):
    """
    Convenience GET endpoint — uses the canonical demo sensor state for the asset.
    Designed for Unity polling and the React dashboard's asset detail panel.
    """
    # Demo sensor states per asset
    _DEMO_SENSORS: Dict[str, Dict[str, float]] = {
        "GDC-WP-007": {"bearing_temp_c": 92.5, "bearing_vibration_mms": 5.8, "steam_inlet_pressure_bar": 26.3},
        "WP-007":     {"bearing_temp_c": 92.5, "bearing_vibration_mms": 5.8, "steam_inlet_pressure_bar": 26.3},
        "GDC-WP-012": {"bearing_temp_c": 78.0, "bearing_vibration_mms": 3.9, "steam_inlet_pressure_bar": 22.0},
    }
    sensor_state = _DEMO_SENSORS.get(asset_id, {
        "bearing_temp_c": 72.0,
        "bearing_vibration_mms": 3.2,
        "steam_inlet_pressure_bar": 20.0,
    })

    req = PredictRequest(asset_id=asset_id, sensor_state=sensor_state)
    return await predict_failure(req)


@router.get(
    "/predict/model/info",
    summary="LSTM model metadata and Watson ML connectivity status",
)
async def predict_model_info():
    """Returns the active inference source and Step 4 training status."""
    watson_configured = bool(_WATSON_ML_URL and _WATSON_ML_API_KEY)
    local_available   = os.path.exists(_LOCAL_H5_PATH)
    tracker_available = _tracker_artifacts_available()

    active_source = "synthetic"
    if watson_configured:
        active_source = "watson_ml (primary)"
    elif tracker_available:
        active_source = "local_tracker_720x8_platt (requires sensor_sequence)"
    elif local_available:
        active_source = "local_h5"

    return {
        "active_source":       active_source,
        "watson_ml_configured": watson_configured,
        "watson_ml_url":        _WATSON_ML_URL or None,
        "local_h5_available":   local_available,
        "local_h5_path":        _LOCAL_H5_PATH,
        "tracker_720x8_available": tracker_available,
        "tracker_model_loaded":    _TRACKER_MODEL is not None,
        "tracker_scaler_loaded":   _TRACKER_SCALER is not None,
        "tracker_calibration_loaded": _TRACKER_CALIBRATION is not None,
        "step_4_complete":      local_available or watson_configured or tracker_available,
        "pending_action": (
            "Train ml/lstm/notebooks/01_lstm_training.ipynb in Watson Studio. "
            "Then either deploy as Watson ML endpoint (set WATSON_ML_URL) "
            "or export lstm_failure.h5 into ml/lstm/models/."
            if not (local_available or watson_configured or tracker_available) else None
        ),
        "timestamp": datetime.now().isoformat(),
    }


# Made with Bob
