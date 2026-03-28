from fastapi import APIRouter

from pydantic import BaseModel

import importlib.util, pathlib


router = APIRouter()


mc_path = pathlib.Path(__file__).parent.parent.parent / 'monte_carlo' / 'engine.py'

spec    = importlib.util.spec_from_file_location('engine', mc_path)

mc_mod  = importlib.util.module_from_spec(spec)

spec.loader.exec_module(mc_mod)


class WhatIfRequest(BaseModel):

    asset_id:         str

    maintenance_date: str   # ISO date: '2026-04-02'


@router.post('/simulate')

async def whatif_simulate(req: WhatIfRequest):

    from api.db.redis_client import get_asset_state

    state = await get_asset_state(req.asset_id)

    if not state: return {'error': 'Asset not found in cache'}

    return mc_mod.whatif_simulation(state['sensors'], req.maintenance_date)


# Made with Bob


@router.get('/alerts')

async def list_alerts(): return get_active_alerts()
