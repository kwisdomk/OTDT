# LSTM Tracker Model Readiness

## Status
The tracker-aligned 720x8 LSTM model has been accepted as the current candidate artifact and is locally usable. An unapproved API wiring attempt (`cb6c0c9b`) was reverted (`b5e2d5f1`, OTD-017). The existing fallback behaviour remains active. Safe API wiring requires explicit approval before implementation.

Platt calibration artifact generated (OTD-019). Calibrated probabilities not yet wired into API or Monte Carlo pipeline. API wiring pending; Monte Carlo integration pending.

## Artifact Paths
- **Model**: `ml/lstm/models/tracker_720x8/lstm_tracker_720x8.keras`
- **Metadata**: `ml/lstm/models/tracker_720x8/lstm_tracker_720x8_metadata.json`
- **Correct Fitted Scaler**: `ml/lstm/models/tracker_720x8/lstm_tracker_720x8_scaler_fitted.pkl`
- **Calibration Artifact**: `ml/lstm/models/tracker_720x8/lstm_tracker_720x8_calibration.json`
- **Original Bad Scaler**: `ml/lstm/models/tracker_720x8/lstm_tracker_720x8_scaler.pkl` (untouched)

Model and scaler binaries are local/external artifacts and are intentionally not committed to Git. The repository currently commits only the metadata and documentation. API wiring requires restoring the .keras model and fitted scaler into the documented local paths.

## Metrics & Verification
- **Test AUC-ROC**: 0.9857
- **Model Input Shape**: `(None, 720, 8)`
- **Scaler Type**: `StandardScaler`
- **Scaler `n_features_in_`**: 8
- **Sample Transformed Prediction**: `0.698833` (succeeded)
- **API Behavior**: Unchanged (fallback remains active; unapproved wiring reverted under OTD-017)

### Platt Calibration Metrics (OTD-019)
- **Equation**: `calibrated_probability = sigmoid(10.2520 * raw_score + (−9.3951))`
- **Raw-score domain**: Model output probability in (0, 1)
- **Brier Score (raw)**: 0.0286
- **Brier Score (calibrated)**: 0.0179 (improved by 0.0107)
- **AUC-ROC (raw)**: 0.9745
- **AUC-ROC (calibrated)**: 0.9745 (unchanged — monotonic transform preserves ranking)
- **Fitted on**: Validation split (1007 windows, 36 positive)
- **Evaluated on**: Test split (1007 windows, 36 positive)

## Known Limitations
- **Synthetic Data**: Trained on synthetic data only.
- **Overlapping Windows**: Sliding windows overlap, meaning the evaluation (AUC-ROC) may be optimistic.
- **Calibration not cross-validated**: Fitted on validation split only.

## Next Steps
- Obtain explicit approval, then implement safe API wiring to replace the fallback mechanism without breaking the demo. The reverted approach is preserved on branch `backup/unapproved-lstm-wiring-cb6c0c9b` for reference.
- Wire calibrated probabilities into Monte Carlo probability inputs (baseline-required integration, not yet approved).
- Export to ONNX and/or SavedModel format.
