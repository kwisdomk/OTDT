from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import date as _date

# Fix: import get_active_alerts so /alerts doesn't crash
from api.integrations.maximo_client import get_active_alerts
from monte_carlo.engine import whatif_simulation

router = APIRouter()


class WhatIfRequest(BaseModel):
    asset_id:         str
    maintenance_date: str   # ISO date: '2026-06-01'


class WhatIfDaysRequest(BaseModel):
    asset_id:         str
    deferral_days:    int = 30  # Number of days to defer maintenance


@router.post('/simulate')
async def whatif_simulate(req: WhatIfRequest):
    """What-If simulation by maintenance date."""
    from api.db.redis_client import get_asset_state
    state = await get_asset_state(req.asset_id)
    if not state:
        state = {}  # Use defaults if asset not yet in cache

    # Convert ISO date string to deferral days (int) for the MC engine
    days = (_date.fromisoformat(req.maintenance_date) - _date.today()).days
    days = max(0, min(days, 180))

    return whatif_simulation(state.get('sensors', {}), days)


@router.post('/simulate-days')
async def whatif_simulate_days(req: WhatIfDaysRequest):
    """What-If simulation by number of days to defer (for slider use)."""
    return whatif_simulation({}, req.deferral_days)


@router.get('/alerts')
async def list_alerts():
    """Get active Maximo Monitor alerts."""
    return get_active_alerts()
