"""
Focused tests for the tracker 720×8 LSTM prediction path in /api/predict/failure.

Validates:
  - WP-07 synthetic fallback is unchanged when no sensor_sequence is sent.
  - Generic asset synthetic fallback is unchanged.
  - Valid 720×8 sensor_sequence with force_source="tracker_lstm" returns
    calibrated prediction with model_source="local_tracker_720x8_platt".
  - Explicit tracker_lstm request without sensor_sequence returns HTTP 422.
  - Explicit tracker_lstm request with wrong shape returns HTTP 422.
  - Explicit tracker_lstm request with missing artifacts returns HTTP 503.
  - Implicit attempt with missing artifacts falls through to synthetic.
  - No sensor_sequence, no force_source → existing behaviour unchanged.

Classification: Supporting implementation (test coverage for OTD-016/OTD-019 wiring).

Requires: pip install -r api/requirements-dev.txt
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch


@pytest.fixture
def app():
    """Import the FastAPI app."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from api.main import app
    return app


# ── Fallback behaviour unchanged ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_wp07_demo_fallback_unchanged(app):
    """WP-07 with no sensor_sequence must return 0.34 synthetic."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/predict/failure", json={
            "asset_id": "GDC-WP-007",
            "sensor_state": {
                "bearing_temp_c": 92.5,
                "bearing_vibration_mms": 5.8,
                "steam_inlet_pressure_bar": 26.3,
            },
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["failure_probability"] == 0.34
    assert data["model_source"] == "synthetic"
    assert data["synthetic"] is True


@pytest.mark.asyncio
async def test_generic_asset_fallback_unchanged(app):
    """Non-hero asset with no sensor_sequence returns synthetic score."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/predict/failure", json={
            "asset_id": "GDC-HX-003",
            "sensor_state": {
                "bearing_temp_c": 72.0,
                "bearing_vibration_mms": 3.2,
                "steam_inlet_pressure_bar": 20.0,
            },
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_source"] == "synthetic"
    assert data["synthetic"] is True
    assert 0.0 < data["failure_probability"] < 1.0


@pytest.mark.asyncio
async def test_no_sensor_sequence_skips_tracker(app):
    """Without sensor_sequence or force_source, tracker path is never entered."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/predict/failure", json={
            "asset_id": "GDC-WP-007",
            "sensor_state": {"bearing_temp_c": 85.0},
        })
    assert resp.status_code == 200
    data = resp.json()
    # Should be synthetic (hero asset override), not tracker
    assert data["model_source"] == "synthetic"


# ── Explicit tracker_lstm error paths ─────────────────────────────────────


@pytest.mark.asyncio
async def test_tracker_lstm_explicit_no_sequence(app):
    """force_source='tracker_lstm' without sensor_sequence → HTTP 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/predict/failure", json={
            "asset_id": "GDC-WP-007",
            "sensor_state": {"bearing_temp_c": 85.0},
            "force_source": "tracker_lstm",
        })
    assert resp.status_code == 422
    assert "sensor_sequence" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_tracker_lstm_wrong_shape_rows(app):
    """force_source='tracker_lstm' with 100×8 sequence → HTTP 422."""
    bad_sequence = [[0.0] * 8 for _ in range(100)]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/predict/failure", json={
            "asset_id": "GDC-WP-007",
            "sensor_state": {"bearing_temp_c": 85.0},
            "force_source": "tracker_lstm",
            "sensor_sequence": bad_sequence,
        })
    assert resp.status_code == 422
    assert "720" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_tracker_lstm_wrong_shape_cols(app):
    """force_source='tracker_lstm' with 720×3 sequence → HTTP 422."""
    bad_sequence = [[0.0] * 3 for _ in range(720)]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/predict/failure", json={
            "asset_id": "GDC-WP-007",
            "sensor_state": {"bearing_temp_c": 85.0},
            "force_source": "tracker_lstm",
            "sensor_sequence": bad_sequence,
        })
    assert resp.status_code == 422
    assert "8 features" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_tracker_lstm_missing_artifacts_explicit(app):
    """force_source='tracker_lstm' with missing model → HTTP 503."""
    valid_sequence = [[1.0] * 8 for _ in range(720)]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("api.routers.predict._TRACKER_MODEL", None):
            resp = await client.post("/api/predict/failure", json={
                "asset_id": "GDC-WP-007",
                "sensor_state": {"bearing_temp_c": 85.0},
                "force_source": "tracker_lstm",
                "sensor_sequence": valid_sequence,
            })
    assert resp.status_code == 503
    assert "not available" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_tracker_lstm_missing_artifacts_implicit(app):
    """Implicit attempt with missing model falls through to synthetic."""
    valid_sequence = [[1.0] * 8 for _ in range(720)]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("api.routers.predict._TRACKER_MODEL", None):
            resp = await client.post("/api/predict/failure", json={
                "asset_id": "GDC-WP-007",
                "sensor_state": {"bearing_temp_c": 85.0},
                "sensor_sequence": valid_sequence,
            })
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_source"] == "synthetic"
    assert data["failure_probability"] == 0.34  # hero asset


# ── Tracker LSTM success path ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tracker_lstm_with_valid_sequence(app):
    """Valid 720×8 sequence with force_source='tracker_lstm' returns calibrated result.

    This test will only pass when all three tracker artifacts are present locally.
    If artifacts are not available, the test is skipped.
    """
    from api.routers.predict import _tracker_artifacts_available
    if not _tracker_artifacts_available():
        pytest.skip("Tracker LSTM artifacts not available locally")

    valid_sequence = [[85.0, 25.0, 4.2, 12.0, 3600.0, 92.0, 84.5, 0.01]] * 720
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/predict/failure", json={
            "asset_id": "GDC-TEST-001",
            "sensor_state": {"bearing_temp_c": 85.0},
            "force_source": "tracker_lstm",
            "sensor_sequence": valid_sequence,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_source"] == "local_tracker_720x8_platt"
    assert data["calibration_applied"] is True
    assert data["is_synthetic"] is False
    assert "raw_score" in data
    assert "calibrated_score" in data
    assert 0.0 < data["failure_probability"] < 1.0
    # failure_probability must be the calibrated value, not the raw score
    assert data["failure_probability"] == round(data["calibrated_score"], 4)


@pytest.mark.asyncio
async def test_tracker_lstm_implicit_with_valid_sequence(app):
    """Implicit attempt with valid sequence and artifacts uses tracker path.

    Skipped if tracker artifacts are not locally available.
    """
    from api.routers.predict import _tracker_artifacts_available
    if not _tracker_artifacts_available():
        pytest.skip("Tracker LSTM artifacts not available locally")

    valid_sequence = [[85.0, 25.0, 4.2, 12.0, 3600.0, 92.0, 84.5, 0.01]] * 720
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/predict/failure", json={
            "asset_id": "GDC-TEST-002",
            "sensor_state": {"bearing_temp_c": 85.0},
            "sensor_sequence": valid_sequence,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_source"] == "local_tracker_720x8_platt"
    assert data["calibration_applied"] is True
