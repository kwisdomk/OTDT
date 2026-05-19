from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import importlib.util, pathlib

# Fix: import get_active_alerts so /alerts doesn't crash
from api.integrations.maximo_client import get_active_alerts

router = APIRouter()

mc_path = pathlib.Path(__file__).parent.parent.parent / 'monte_carlo' / 'engine.py'
spec    = importlib.util.spec_from_file_location('engine', mc_path)
mc_mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc_mod)


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
    return mc_mod.whatif_simulation(state.get('sensors', {}), req.maintenance_date)


@router.post('/simulate-days')
async def whatif_simulate_days(req: WhatIfDaysRequest):
    """What-If simulation by number of days to defer (for slider use)."""
    return mc_mod.whatif_simulation({}, req.deferral_days)


@router.get('/alerts')
async def list_alerts():
    """Get active Maximo Monitor alerts."""
    return get_active_alerts()
