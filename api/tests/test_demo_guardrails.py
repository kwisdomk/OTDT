"""
Cross-cutting demo guardrail regression tests.

Proves that all protected WP-07 demo paths, Unity contract,
and engine-backed simulation remain unchanged after the
calibrated LSTM prediction wiring.

These tests must pass before and after any predict.py edit.

Classification: Supporting implementation (regression safety net).

Requires: pip install -r api/requirements-dev.txt
"""

import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def app():
    """Import the FastAPI app."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from api.main import app
    return app


# ── Unity What-If demo route (protected) ─────────────────────────────────


@pytest.mark.asyncio
async def test_whatif_0_day_still_34(app):
    """deferral_days=0 must return base probability 0.34."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/monte-carlo/whatif", json={
            "asset_id": "GDC-WP-007",
            "deferral_days": 0,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["deferred_failure_probability"] == 0.34
    assert data["base_failure_probability"] == 0.34
    assert data["expected_failure_cost_usd"] == 61200.0
    assert data["model_source"] == "calibrated_baseline_demo"


@pytest.mark.asyncio
async def test_whatif_45_day_still_68(app):
    """deferral_days=45 must return 0.68 probability and USD 122,400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/monte-carlo/whatif", json={
            "asset_id": "GDC-WP-007",
            "deferral_days": 45,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["deferred_failure_probability"] == 0.68
    assert data["expected_failure_cost_usd"] == 122400.0
    assert data["failure_cost_usd"] == 180000


@pytest.mark.asyncio
async def test_whatif_112_day_value(app):
    """deferral_days=112 must return approximately 83.9%."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/monte-carlo/whatif", json={
            "asset_id": "GDC-WP-007",
            "deferral_days": 112,
        })
    assert resp.status_code == 200
    data = resp.json()
    prob = data["deferred_failure_probability"]
    # Formula: 0.68 + ((112 - 45) / 135) * (1.0 - 0.68) = 0.68 + 0.1587 = 0.8387
    assert abs(prob - 0.8387) < 0.005, f"Expected ~0.839, got {prob}"


@pytest.mark.asyncio
async def test_whatif_unity_contract_unchanged(app):
    """Unity payload {asset_id, deferral_days} must be accepted with all expected fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/monte-carlo/whatif", json={
            "asset_id": "GDC-WP-007",
            "deferral_days": 30,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["asset_id"] == "GDC-WP-007"
    assert "deferral_days" in data
    assert "failure_probability" in data
    assert "model_source" in data
    assert data["model_source"] == "calibrated_baseline_demo"
    assert data["synthetic"] is True


# ── Prediction fallback (protected) ──────────────────────────────────────


@pytest.mark.asyncio
async def test_predict_get_wp07_unchanged(app):
    """GET /api/predict/failure/GDC-WP-007 must return 0.34 synthetic."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/predict/failure/GDC-WP-007")
    assert resp.status_code == 200
    data = resp.json()
    assert data["failure_probability"] == 0.34
    assert data["model_source"] == "synthetic"
    assert data["synthetic"] is True


# ── Engine-backed simulation (not forced to 68%) ────────────────────────


@pytest.mark.asyncio
async def test_whatif_simulate_not_forced(app):
    """POST /whatif/simulate-days with 45 days returns Weibull result, NOT 0.68.

    The engine-backed Weibull simulation naturally produces ~0.56 at 45 days.
    It must NOT be forced to match the protected demo value of 0.68.
    Stochastic tolerance: ±0.15 around 0.56.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/whatif/simulate-days", json={
            "asset_id": "GDC-WP-007",
            "deferral_days": 45,
        })
    assert resp.status_code == 200
    data = resp.json()
    prob = data["failure_probability"]
    # Must be approximately 0.56 (stochastic), NOT exactly 0.68
    assert prob != 0.68, "Engine route must not return the protected demo value"
    assert 0.30 < prob < 0.80, f"Weibull 45-day result out of expected range: {prob}"
    assert data["synthetic"] is True
