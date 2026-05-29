from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_predict_failure_synthetic_fallback_post():
    payload = {
        "asset_id": "GDC-WP-007",
        "sensor_state": {"bearing_temp_c": 92.5},
        "force_source": "synthetic"
    }
    response = client.post("/api/predict/failure", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["failure_probability"] == 0.34
    assert data["model_source"] == "synthetic"

def test_predict_failure_force_tracker_missing_sequence():
    payload = {
        "asset_id": "TEST-01",
        "sensor_state": {"bearing_temp_c": 90.0},
        "force_source": "local_tracker_720x8"
    }
    response = client.post("/api/predict/failure", json=payload)
    assert response.status_code == 422
    assert "sensor_sequence is required" in response.text

def test_predict_failure_invalid_sequence_shape():
    payload = {
        "asset_id": "TEST-01",
        "sensor_state": {"bearing_temp_c": 90.0},
        "sensor_sequence": [[1.0, 2.0]]
    }
    response = client.post("/api/predict/failure", json=payload)
    assert response.status_code == 422
    assert "shape must be (720, 8)" in response.text

def test_predict_failure_valid_sequence_unavailable_model(monkeypatch):
    from api.routers import predict as predict_router

    monkeypatch.setattr(predict_router, "_TRACKER_MODEL", None)
    monkeypatch.setattr(predict_router, "_TRACKER_SCALER", None)

    payload = {
        "asset_id": "TEST-01",
        "sensor_state": {"bearing_temp_c": 90.0},
        "sensor_sequence": [[0.0] * 8 for _ in range(720)]
    }
    response = client.post("/api/predict/failure", json=payload)
    assert response.status_code == 500
    assert "artifacts unavailable" in response.text

def test_predict_model_info_includes_tracker_fields():
    response = client.get("/api/predict/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "tracker_720x8_available" in data
    assert "tracker_720x8_metadata_available" in data
    assert "tracker_720x8_model_path" in data
