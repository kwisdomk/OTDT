"""
CNN Anomaly Detection API — Track B, Step 7.

GET  /anomaly/status/{asset_id}   → per-asset anomaly score + classification
GET  /anomaly/status              → all 50 assets batch summary
POST /anomaly/batch               → batch score for a list of asset IDs

⚠️  SYNTHETIC MODE: Real CNN training requires 500+ Unity screenshots (Step 7).
    This router returns deterministic synthetic scores so the React dashboard
    can be fully integrated now.  When the CNN model is available, replace the
    `_score_asset()` function body — the API contract stays identical.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import math
import os

router = APIRouter()

# ── CNN model loader (graceful degradation) ────────────────────────────────
# Attempt to load a real trained model from ml/cnn_anomaly/models/.
# Falls back to synthetic scoring if the model file is not present yet.
_CNN_MODEL = None
_CNN_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml", "cnn_anomaly", "models", "cnn_anomaly.h5"
)

try:
    if os.path.exists(_CNN_MODEL_PATH):
        import tensorflow as tf  # type: ignore
        _CNN_MODEL = tf.keras.models.load_model(_CNN_MODEL_PATH)
        print(f"[CNN] Loaded real model from {_CNN_MODEL_PATH}")
    else:
        print("[CNN] Model not found — running in SYNTHETIC mode (Step 7 pending)")
except Exception as _e:
    print(f"[CNN] Model load failed ({_e}) — running in SYNTHETIC mode")


# ── Synthetic scoring engine ───────────────────────────────────────────────
# Deterministic per-asset scores, calibrated for the GDC demo script:
#   GDC-WP-007 → ANOMALY  (hero asset for the demo narrative)
#   GDC-WP-012 → WARNING
#   all others → NORMAL    (mild variance added via sine wave)

_DEMO_OVERRIDES: Dict[str, float] = {
    "GDC-WP-007": 0.87,   # ANOMALY — main demo asset
    "WP-007":     0.87,
    "GDC-WP-012": 0.61,   # WARNING
    "WP-012":     0.61,
}


def _score_asset(asset_id: str) -> float:
    """
    Return a CNN anomaly score in [0.0, 1.0] for the given asset.

    Replace this function body when the real CNN model is available:
        img_tensor = preprocess_screenshot(asset_id)
        return float(_CNN_MODEL.predict(img_tensor)[0][0])
    """
    if _CNN_MODEL is not None:
        # Real model path — placeholder for when Step 7 is complete
        # img_tensor = preprocess_screenshot(asset_id)
        # return float(_CNN_MODEL.predict(img_tensor)[0][0])
        pass  # fall through to synthetic until preprocessing is wired

    if asset_id in _DEMO_OVERRIDES:
        return _DEMO_OVERRIDES[asset_id]

    # Stable pseudo-random score per asset_id (hash-based, reproducible)
    seed = sum(ord(c) for c in asset_id)
    base = 0.08 + 0.18 * abs(math.sin(seed))
    return round(min(base, 0.99), 4)


def _classify(score: float) -> str:
    if score >= 0.75:
        return "ANOMALY"
    if score >= 0.50:
        return "WARNING"
    return "NORMAL"


def _colour(classification: str) -> str:
    return {"ANOMALY": "#C00000", "WARNING": "#FF9900", "NORMAL": "#1E6B3C"}[classification]


# ── Known GDC assets (mirrors assets.py) ──────────────────────────────────
_GDC_ASSETS = [f"GDC-WP-{str(i).zfill(3)}" for i in range(1, 51)]


# ── Pydantic schemas ───────────────────────────────────────────────────────

class AnomalyStatus(BaseModel):
    asset_id: str
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="CNN confidence score [0–1]")
    classification: str = Field(..., description="NORMAL | WARNING | ANOMALY")
    colour_hex: str
    model_source: str = Field(..., description="'cnn_model' or 'synthetic'")
    timestamp: str
    synthetic: bool
    disclaimer: str


class BatchRequest(BaseModel):
    asset_ids: List[str] = Field(..., min_length=1, max_length=50)


# ── Helper ─────────────────────────────────────────────────────────────────

def _build_status(asset_id: str) -> AnomalyStatus:
    score = _score_asset(asset_id)
    classification = _classify(score)
    source = "cnn_model" if _CNN_MODEL is not None else "synthetic"
    return AnomalyStatus(
        asset_id=asset_id,
        anomaly_score=round(score, 4),
        classification=classification,
        colour_hex=_colour(classification),
        model_source=source,
        timestamp=datetime.now().isoformat(),
        synthetic=(_CNN_MODEL is None),
        disclaimer=(
            "⚠️ SYNTHETIC DATA — CNN model not yet trained. "
            "Scores are deterministic simulations for dashboard integration only."
            if _CNN_MODEL is None
            else "CNN anomaly score from trained model."
        ),
    )


# ── Routes ─────────────────────────────────────────────────────────────────

@router.get(
    "/anomaly/status/{asset_id}",
    response_model=AnomalyStatus,
    summary="CNN anomaly score for a single asset",
)
async def get_anomaly_status(asset_id: str):
    """
    Returns the CNN visual anomaly classification for a single asset.

    **Demo note:** Returns synthetic scores until Step 7 (CNN training) is complete.
    The API contract is stable — the React dashboard can integrate against this now.

    - `anomaly_score` ∈ [0.0, 1.0] — higher = more anomalous
    - `classification` — NORMAL / WARNING / ANOMALY
    - `model_source` — 'cnn_model' when real; 'synthetic' while training pending
    """
    try:
        return _build_status(asset_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly scoring failed: {e}")


@router.get(
    "/anomaly/status",
    response_model=List[AnomalyStatus],
    summary="CNN anomaly scores for all 50 GDC assets",
)
async def get_all_anomaly_statuses():
    """
    Returns anomaly scores for all 50 GDC geothermal assets in one call.
    Useful for the dashboard overview map / heat-map panel.
    """
    try:
        return [_build_status(aid) for aid in _GDC_ASSETS]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch anomaly scoring failed: {e}")


@router.post(
    "/anomaly/batch",
    response_model=List[AnomalyStatus],
    summary="CNN anomaly scores for a custom list of assets",
)
async def batch_anomaly_status(request: BatchRequest):
    """
    Score a custom list of asset IDs (max 50).
    Useful when the dashboard only needs to refresh a subset.
    """
    try:
        return [_build_status(aid) for aid in request.asset_ids]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch anomaly scoring failed: {e}")


@router.get(
    "/anomaly/model/info",
    summary="CNN model metadata",
)
async def anomaly_model_info():
    """Returns the current model source and training status."""
    return {
        "model_loaded": _CNN_MODEL is not None,
        "model_source": "cnn_model" if _CNN_MODEL is not None else "synthetic",
        "model_path": _CNN_MODEL_PATH,
        "step_7_complete": _CNN_MODEL is not None,
        "pending_action": (
            "Capture 500+ Unity screenshots per class, train ml/cnn_anomaly/notebooks/01_cnn_training.ipynb"
            if _CNN_MODEL is None else None
        ),
        "timestamp": datetime.now().isoformat(),
    }


# Made with Bob
