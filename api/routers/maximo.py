"""
Maximo API endpoints.
"""

from fastapi import APIRouter
from api.integrations.maximo_client import get_active_alerts, create_work_order

router = APIRouter()

@router.get('/alerts')
async def list_alerts():
    """Get active Maximo Monitor alerts."""
    return get_active_alerts()

@router.post('/workorder')
async def create_wo(asset_id: str, prob: float, scheduled_date: str):
    """Manually create a work order (for testing)."""
    return create_work_order(asset_id, prob, scheduled_date)