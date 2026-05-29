# LSTM Tracker Model Readiness

## Status
The tracker-aligned 720x8 LSTM model has been accepted as the current candidate artifact and is locally usable. Safe API wiring is currently pending.

## Artifact Paths
- **Model**: `ml/lstm/models/tracker_720x8/lstm_tracker_720x8.keras`
- **Metadata**: `ml/lstm/models/tracker_720x8/lstm_tracker_720x8_metadata.json`
- **Correct Fitted Scaler**: `ml/lstm/models/tracker_720x8/lstm_tracker_720x8_scaler_fitted.pkl`
- **Original Bad Scaler**: `ml/lstm/models/tracker_720x8/lstm_tracker_720x8_scaler.pkl` (untouched)

Model and scaler binaries are local/external artifacts and are intentionally not committed to Git. The repository currently commits only the metadata and documentation. API wiring requires restoring the .keras model and fitted scaler into the documented local paths.

## Metrics & Verification
- **Test AUC-ROC**: 0.9857
- **Model Input Shape**: `(None, 720, 8)`
- **Scaler Type**: `StandardScaler`
- **Scaler `n_features_in_`**: 8
- **Sample Transformed Prediction**: `0.698833` (succeeded)
- **API Behavior**: Unchanged (fallback remains active)

## Known Limitations
- **Synthetic Data**: Trained on synthetic data only.
- **Overlapping Windows**: Sliding windows overlap, meaning the evaluation (AUC-ROC) may be optimistic.

## Next Steps
- Implement safe API wiring to replace the fallback mechanism without breaking the demo.
- Export to ONNX and/or SavedModel format.
- Perform Platt calibration for the model output probabilities.
