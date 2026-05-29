"""
Focused tests for /api/monte-carlo/whatif endpoint.

Validates the calibrated baseline demo contract:
  - deferral_days = 0  → 34% failure probability
  - deferral_days = 45 → 68% failure probability, USD 122,400 expected cost
  - maintenance_date equivalent to 45-day deferral → same result
  - Unity-shaped payload (asset_id + deferral_days) is accepted
  - Backward-compatible fields are preserved

Classification: Supporting implementation (test coverage for OTD-009 fix).
"""

import pytest
from httpx import AsyncClient, ASGITransport
from datetime import date, timedelta


@pytest.fixture
def app():
    """Import the FastAPI app."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from api.main import app
    return app


@pytest.mark.asyncio
async def test_whatif_deferral_zero_days(app):
    """deferral_days=0 should return base probability 0.34."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/monte-carlo/whatif", json={
            "asset_id": "GDC-WP-007",
            "deferral_days": 0
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["asset_id"] == "GDC-WP-007"
    assert data["deferral_days"] == 0
    assert data["base_failure_probability"] == 0.34
    assert data["deferred_failure_probability"] == 0.34
    assert data["failure_cost_usd"] == 180000
    assert data["expected_failure_cost_usd"] == 61200.0
    assert data["inspection_cost_usd"] == 8000
    assert data["model_source"] == "calibrated_baseline_demo"


@pytest.mark.asyncio
async def test_whatif_deferral_45_days(app):
    """deferral_days=45 should return 0.68 probability and USD 122,400 expected cost."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/monte-carlo/whatif", json={
            "asset_id": "GDC-WP-007",
            "deferral_days": 45
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["deferral_days"] == 45
    assert data["deferred_failure_probability"] == 0.68
    assert data["expected_failure_cost_usd"] == 122400.0
    assert data["failure_cost_usd"] == 180000
    assert data["recommendation"] == "URGENT"


@pytest.mark.asyncio
async def test_whatif_maintenance_date_45_days(app):
    """maintenance_date 45 days from today should produce the same 0.68 / 122400 result."""
    future_date = (date.today() + timedelta(days=45)).isoformat()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/monte-carlo/whatif", json={
            "asset_id": "GDC-WP-007",
            "maintenance_date": future_date
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["deferral_days"] == 45
    assert data["deferred_failure_probability"] == 0.68
    assert data["expected_failure_cost_usd"] == 122400.0


@pytest.mark.asyncio
async def test_whatif_unity_payload_accepted(app):
    """Unity sends {asset_id, deferral_days} — must be accepted without error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/monte-carlo/whatif", json={
            "asset_id": "GDC-WP-007",
            "deferral_days": 30
        })
    assert resp.status_code == 200
    data = resp.json()
    # Unity reads failure_probability (backward-compat field)
    assert "failure_probability" in data
    assert "deferral_days" in data
    assert data["asset_id"] == "GDC-WP-007"


@pytest.mark.asyncio
async def test_whatif_backward_compat_fields(app):
    """Backward-compatible fields must still be present for React/API callers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/monte-carlo/whatif", json={
            "asset_id": "GDC-WP-007",
            "deferral_days": 45
        })
    assert resp.status_code == 200
    data = resp.json()
    # New fields
    assert "base_failure_probability" in data
    assert "deferred_failure_probability" in data
    assert "failure_cost_usd" in data
    assert "expected_failure_cost_usd" in data
    assert "inspection_cost_usd" in data
    assert "recommendation" in data
    assert "model_source" in data
    # Legacy fields preserved
    assert "failure_probability" in data
    assert "recommended_action" in data
    assert "expected_cost_usd" in data
    assert "maintenance_deferral_days" in data
    assert "maintenance_date" in data
    assert data["synthetic"] is True


@pytest.mark.asyncio
async def test_whatif_no_params_defaults_zero(app):
    """If neither deferral_days nor maintenance_date provided, default to 0 days."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/monte-carlo/whatif", json={
            "asset_id": "GDC-WP-007"
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["deferral_days"] == 0
    assert data["deferred_failure_probability"] == 0.34
