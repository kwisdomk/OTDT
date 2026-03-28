"""
Maximo API endpoints.

Build Guide Step 2: Asset inventory and work order management.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from maximo.asset_loader import AssetLoader
from api.integrations.maximo_client import get_active_alerts, create_work_order

router = APIRouter()

# Initialize asset loader (singleton pattern)
_asset_loader = None

def get_asset_loader() -> AssetLoader:
    """Get or create asset loader instance."""
    global _asset_loader
    if _asset_loader is None:
        _asset_loader = AssetLoader(mock_mode=True)
        try:
            _asset_loader.load_from_excel()
        except Exception as e:
            print(f"Warning: Could not load assets from Excel: {e}")
    return _asset_loader


@router.get('/assets')
async def list_assets(
    asset_class: Optional[str] = Query(None, description="Filter by asset class (WELL_PUMP, HEAT_EXCHANGER, TURBINE, PRODUCTION_PIPE)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Get GDC Kenya asset inventory.
    
    Build Guide Step 2 (Line 204): Expose asset inventory to Unity 3D model.
    
    Returns:
        Asset list with synthetic data disclaimer
    """
    loader = get_asset_loader()
    
    # Filter by asset class if specified
    if asset_class:
        valid_classes = ["WELL_PUMP", "HEAT_EXCHANGER", "TURBINE", "PRODUCTION_PIPE"]
        if asset_class not in valid_classes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid asset_class. Must be one of: {', '.join(valid_classes)}"
            )
        assets = loader.get_assets_by_class(asset_class)
    else:
        assets = loader.assets
    
    # Apply pagination
    total = len(assets)
    paginated_assets = assets[offset:offset + limit]
    
    return {
        "assets": paginated_assets,
        "total": total,
        "filtered": asset_class is not None,
        "filter": {"asset_class": asset_class, "limit": limit, "offset": offset} if asset_class else None,
        "disclaimer": "⚠️ SYNTHETIC DATA: All readings are computer-generated. Not representative of any real client operational data."
    }


@router.get('/assets/{asset_id}')
async def get_asset(asset_id: str):
    """Get a single asset by ID.
    
    Args:
        asset_id: Asset identifier (e.g., GDC-WP-007)
        
    Returns:
        Asset details or 404 if not found
    """
    loader = get_asset_loader()
    asset = loader.get_asset_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset {asset_id} not found",
        )
    
    return {
        "asset": asset,
        "disclaimer": "⚠️ SYNTHETIC DATA: All readings are computer-generated."
    }


@router.get('/alerts')
async def list_alerts():
    """Get active Maximo Monitor alerts."""
    return get_active_alerts()


@router.post('/workorder')
async def create_wo(asset_id: str, prob: float, scheduled_date: str):
    """Manually create a work order (for testing)."""
    return create_work_order(asset_id, prob, scheduled_date)