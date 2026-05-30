"""
Create Platt calibration artifact for the tracker-aligned 720x8 LSTM model.

Reads OT_Digital_Twin_MVP_Tracker.xlsx -> Sensor_Readings,
recreates the same 720x8 feature engineering and sliding-window logic
used for the tracker model, loads the local model and fitted scaler,
generates raw predictions on validation and test splits,
fits Platt calibration on validation predictions only,
evaluates on test predictions, and writes a calibration JSON artifact.

Equation (Option A — approved OTD-019):
    calibrated_probability = sigmoid(coefficient * raw_score + intercept)
    where sigmoid(x) = 1 / (1 + exp(-x))
    raw_score = raw model output probability in [0, 1]

Usage (from repo root):
    .\\venv\\Scripts\\python.exe ml/lstm/scripts/create_platt_calibration.py
"""

import json
import os
import pickle
import sys
from datetime import datetime, timezone

# TensorFlow MUST be imported before scikit-learn in this environment.
# TF 2.16.1 + sklearn 1.4.2 on Python 3.11.9/Windows crashes if sklearn
# is imported first (hard process kill, no Python traceback).
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # suppress TF C++ info/warning
import tensorflow as tf  # noqa: E402

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ── Paths ──────────────────────────────────────────────────────────────────
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TRACKER = os.path.join(REPO_ROOT, "OT_Digital_Twin_MVP_Tracker.xlsx")
MODEL_DIR = os.path.join(REPO_ROOT, "ml", "lstm", "models", "tracker_720x8")
META_PATH = os.path.join(MODEL_DIR, "lstm_tracker_720x8_metadata.json")
MODEL_PATH = os.path.join(MODEL_DIR, "lstm_tracker_720x8.keras")
SCALER_PATH = os.path.join(MODEL_DIR, "lstm_tracker_720x8_scaler_fitted.pkl")
CALIB_OUT = os.path.join(MODEL_DIR, "lstm_tracker_720x8_calibration.json")

FEATURES = [
    "temperature_c",
    "pressure_bar",
    "vibration_mm_s",
    "flow_rate_kg_s",
    "rotation_rpm",
    "health_score",
    "rolling_7d_temp_mean",
    "rate_of_change_vibration",
]

SEQ_LEN = 720
STRIDE = 12
TRAIN_FRAC = 0.70
VAL_FRAC = 0.15
# test is the remaining 0.15


# ── Data loading ───────────────────────────────────────────────────────────

def load_and_clean() -> pd.DataFrame:
    """Load Sensor_Readings with header=1, drop rows without timestamp/asset."""
    print("[1/8] Loading Sensor_Readings from tracker ...")
    df = pd.read_excel(TRACKER, sheet_name="Sensor_Readings", header=1)
    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    # Keep only rows that have both a parseable timestamp and an asset_id
    df = df.dropna(subset=["timestamp", "asset_id"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values(["asset_id", "timestamp"]).reset_index(drop=True)
    print(f"       -> {len(df)} clean rows, {df['asset_id'].nunique()} assets")
    return df


# ── Feature engineering ────────────────────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add rolling_7d_temp_mean and rate_of_change_vibration per asset."""
    print("[2/8] Engineering features ...")
    # rolling_7d_temp_mean: 168-hour rolling mean of temperature_c per asset
    df["rolling_7d_temp_mean"] = (
        df.groupby("asset_id")["temperature_c"]
        .transform(lambda s: s.rolling(168, min_periods=1).mean())
    )
    # rate_of_change_vibration: per-asset diff, first value filled with 0
    df["rate_of_change_vibration"] = (
        df.groupby("asset_id")["vibration_mm_s"]
        .transform(lambda s: s.diff().fillna(0))
    )
    # Verify all feature columns present
    missing = [f for f in FEATURES if f not in df.columns]
    if missing:
        sys.exit(f"FATAL: missing columns after engineering: {missing}")
    print("       -> features OK")
    return df


# ── Label creation ─────────────────────────────────────────────────────────

def create_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Create future_failure_30d: 1 if any failure_event==1 within next 720 rows."""
    print("[3/8] Creating future_failure_30d labels ...")
    if "failure_event" not in df.columns:
        sys.exit("FATAL: 'failure_event' column not found in Sensor_Readings")

    df["failure_event"] = df["failure_event"].fillna(0).astype(int)
    labels = []
    for _aid, grp in df.groupby("asset_id"):
        fe = grp["failure_event"].values
        n = len(fe)
        future_fail = np.zeros(n, dtype=int)
        # Reverse cumulative scan: check if any failure_event==1 in next 720 rows
        # Use a rolling sum on the reversed array for efficiency
        fe_reversed = fe[::-1]
        cumsum_rev = np.cumsum(fe_reversed)
        for i in range(n):
            # rows ahead: i+1 to i+720 (inclusive), which is fe[i+1:i+721]
            end_idx = min(i + SEQ_LEN, n - 1)
            if i < n - 1:
                # sum of failure_event from i+1 to end_idx (inclusive)
                s = cumsum_rev[n - 1 - (i + 1)] - (cumsum_rev[n - 1 - (end_idx + 1)] if end_idx + 1 < n else 0) if i + 1 <= end_idx else 0
                # Simpler approach: just use direct slicing
                future_fail[i] = 1 if np.any(fe[i + 1: i + 1 + SEQ_LEN]) else 0
            else:
                future_fail[i] = 0
        labels.append(pd.Series(future_fail, index=grp.index))

    df["future_failure_30d"] = pd.concat(labels)
    pos = df["future_failure_30d"].sum()
    print(f"       -> {pos} positive labels out of {len(df)} rows")
    return df


# ── Sliding windows ───────────────────────────────────────────────────────

def create_windows(df: pd.DataFrame):
    """Create sliding windows of SEQ_LEN with STRIDE, per asset."""
    print("[4/8] Creating sliding windows ...")
    all_X = []
    all_y = []

    for _aid, grp in df.groupby("asset_id"):
        feat_vals = grp[FEATURES].values
        label_vals = grp["future_failure_30d"].values
        n = len(grp)
        for start in range(0, n - SEQ_LEN + 1, STRIDE):
            end = start + SEQ_LEN
            all_X.append(feat_vals[start:end])
            # Label = label at the last row of the window
            all_y.append(label_vals[end - 1])

    X = np.array(all_X, dtype=np.float64)
    y = np.array(all_y, dtype=np.int32)
    print(f"       -> {len(X)} total windows, {y.sum()} positive")
    return X, y


# ── Train/val/test split ──────────────────────────────────────────────────

def split_windows(df: pd.DataFrame):
    """Create sliding windows and split with stratification.

    The metadata documents 'stratified sliding windows, stride 12 hours'.
    A purely chronological split concentrates all positive labels in the
    early portion, leaving test with 0 positives.  Stratified splitting
    ensures each split receives positive samples, matching the metadata
    counts (train_positive=169, validation_positive=36, test_positive=36).
    """
    print("[4/8] Creating sliding windows ...")
    sys.stdout.flush()

    all_X = []
    all_y = []

    for _aid, grp in df.groupby("asset_id"):
        feat_vals = grp[FEATURES].values
        label_vals = grp["future_failure_30d"].values
        n = len(grp)
        for start in range(0, n - SEQ_LEN + 1, STRIDE):
            end = start + SEQ_LEN
            all_X.append(feat_vals[start:end])
            all_y.append(label_vals[end - 1])

    X = np.array(all_X, dtype=np.float64)
    y = np.array(all_y, dtype=np.int32)
    print(f"       -> {len(X)} total windows, {y.sum()} positive")

    print("[5/8] Stratified split into train/val/test ...")
    sys.stdout.flush()

    # First split: 70% train, 30% temp (val + test)
    train_X, temp_X, train_y, temp_y = train_test_split(
        X, y, test_size=(1 - TRAIN_FRAC), stratify=y, random_state=42
    )
    # Second split: 50/50 of the 30% -> 15% val, 15% test
    val_X, test_X, val_y, test_y = train_test_split(
        temp_X, temp_y, test_size=0.5, stratify=temp_y, random_state=42
    )

    print(f"       -> train: {len(train_X)} ({train_y.sum()} pos)")
    print(f"       -> val:   {len(val_X)} ({val_y.sum()} pos)")
    print(f"       -> test:  {len(test_X)} ({test_y.sum()} pos)")
    sys.stdout.flush()
    return train_X, train_y, val_X, val_y, test_X, test_y


# ── Platt calibration math ────────────────────────────────────────────────

def platt_sigmoid(raw_score: float, coefficient: float, intercept: float) -> float:
    """Apply Platt calibration: sigmoid(coefficient * raw_score + intercept).

    Uses the explicit convention approved under OTD-019:
        calibrated_probability = sigmoid(coefficient * raw_score + intercept)
        where sigmoid(x) = 1 / (1 + exp(-x))
        raw_score is the raw model output probability in [0, 1].
    """
    x = coefficient * raw_score + intercept
    return 1.0 / (1.0 + np.exp(-x))


def platt_sigmoid_array(raw_scores: np.ndarray, coefficient: float, intercept: float) -> np.ndarray:
    """Vectorised Platt calibration on an array of raw scores."""
    x = coefficient * raw_scores + intercept
    return 1.0 / (1.0 + np.exp(-x))


# ── Main pipeline ─────────────────────────────────────────────────────────

def main():
    # ── Check prerequisites ────────────────────────────────────────────
    for path, label in [
        (TRACKER, "Tracker workbook"),
        (MODEL_PATH, "LSTM .keras model"),
        (SCALER_PATH, "Fitted scaler .pkl"),
        (META_PATH, "Metadata JSON"),
    ]:
        if not os.path.isfile(path):
            sys.exit(f"FATAL: {label} not found at {path}")
    print("[0/8] All prerequisites present.\n")

    # ── Load TF model and scaler FIRST (before large data arrays) ───────
    # TF model loading is done before data processing to avoid memory
    # pressure: the windowing step creates ~300 MB of numpy arrays and
    # loading TF on top of that causes a silent process kill on Windows.
    print("[1/8] Loading fitted scaler and model ...")
    sys.stdout.flush()

    with open(SCALER_PATH, "rb") as f:
        scaler: StandardScaler = pickle.load(f)
    print(f"       -> scaler n_features_in_={scaler.n_features_in_}")
    sys.stdout.flush()

    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print(f"       -> model input shape: {model.input_shape}")
    sys.stdout.flush()

    # ── Load and prepare data ──────────────────────────────────────────
    df = load_and_clean()
    df = engineer_features(df)
    df = create_labels(df)

    # ── Split into train/val/test ──────────────────────────────────────
    _train_X, _train_y, val_X, val_y, test_X, test_y = split_windows(df)
    del _train_X, _train_y, df  # free memory not needed for calibration

    # ── Scale and predict on validation ────────────────────────────────
    print("[7/8] Generating predictions ...")

    def predict_split(X_raw: np.ndarray, split_name: str) -> np.ndarray:
        """Scale windows and generate raw model predictions."""
        n_samples = X_raw.shape[0]
        # Reshape to 2D for scaler, scale, reshape back
        X_2d = X_raw.reshape(-1, 8)
        X_scaled_2d = scaler.transform(X_2d)
        X_scaled = X_scaled_2d.reshape(n_samples, SEQ_LEN, 8).astype("float32")
        preds = model.predict(X_scaled, verbose=0, batch_size=256)
        raw_scores = preds.flatten()
        print(f"       -> {split_name}: {n_samples} predictions, "
              f"range [{raw_scores.min():.6f}, {raw_scores.max():.6f}]")
        sys.stdout.flush()
        return raw_scores

    val_raw = predict_split(val_X, "validation")
    test_raw = predict_split(test_X, "test")

    # ── Fit Platt calibration on validation ────────────────────────────
    print("[8/8] Fitting Platt calibration on validation split ...")

    # Option A: fit logistic regression directly on raw model probabilities
    # LogisticRegression with very high C (no regularisation) on raw_score -> label
    lr = LogisticRegression(C=1e10, solver="lbfgs", max_iter=10000)
    lr.fit(val_raw.reshape(-1, 1), val_y)

    coefficient = float(lr.coef_[0][0])
    intercept_val = float(lr.intercept_[0])
    print(f"       -> coefficient: {coefficient:.6f}")
    print(f"       -> intercept:   {intercept_val:.6f}")

    # ── Evaluate on test split ─────────────────────────────────────────
    print("\n--- Test-split evaluation ---")

    # Raw metrics
    brier_raw = float(brier_score_loss(test_y, test_raw))
    auc_raw = float(roc_auc_score(test_y, test_raw))
    print(f"   Raw      Brier: {brier_raw:.6f}   AUC-ROC: {auc_raw:.6f}")

    # Calibrated metrics
    test_calibrated = platt_sigmoid_array(test_raw, coefficient, intercept_val)
    brier_cal = float(brier_score_loss(test_y, test_calibrated))
    auc_cal = float(roc_auc_score(test_y, test_calibrated))
    print(f"   Calibr.  Brier: {brier_cal:.6f}   AUC-ROC: {auc_cal:.6f}")

    if brier_cal < brier_raw:
        print(f"   -> Brier IMPROVED by {brier_raw - brier_cal:.6f}")
    elif brier_cal > brier_raw:
        print(f"   -> Brier WORSENED by {brier_cal - brier_raw:.6f}")
    else:
        print(f"   -> Brier UNCHANGED")

    # ── Write calibration JSON ─────────────────────────────────────────
    print(f"\nWriting calibration artifact -> {CALIB_OUT}")

    calib = {
        "method": "platt_scaling",
        "equation": (
            "calibrated_probability = sigmoid(coefficient * raw_score + intercept) "
            "where sigmoid(x) = 1 / (1 + exp(-x))"
        ),
        "coefficient": coefficient,
        "intercept": intercept_val,
        "fitted_on_split": "validation",
        "evaluated_on_split": "test",
        "raw_score_domain": "probability (0, 1)",
        "brier_score_raw": brier_raw,
        "brier_score_calibrated": brier_cal,
        "auc_roc_raw": auc_raw,
        "auc_roc_calibrated": auc_cal,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_metadata_file": "lstm_tracker_720x8_metadata.json",
        "source_workbook": "OT_Digital_Twin_MVP_Tracker.xlsx",
        "feature_names": FEATURES,
        "sequence_length": SEQ_LEN,
        "known_limitations": [
            "Synthetic data only",
            "Sliding windows overlap, so evaluation may be optimistic",
            "Calibration fitted on validation split only, not cross-validated",
            "Not yet wired into API or Monte Carlo pipeline",
        ],
    }

    with open(CALIB_OUT, "w") as f:
        json.dump(calib, f, indent=2)
    print(f"       -> {os.path.getsize(CALIB_OUT)} bytes written")
    print("\n[DONE] Calibration artifact generated successfully.")


if __name__ == "__main__":
    main()
