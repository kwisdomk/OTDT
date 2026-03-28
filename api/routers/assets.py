"""
Assets API endpoints.

Provides access to all 50 GDC assets from GDC_Assets.xlsx.
Unity SensorBridge.cs polls these endpoints for asset data.

⚠️ SYNTHETIC DATA: All readings are computer-generated.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from maximo.asset_loader import AssetLoader

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
            print(f"Warning: Could not load assets: {e}")
    return _asset_loader


@router.get('/assets')
async def get_all_assets():
    """Get all 50 GDC assets.
    
    Build Guide: Unity needs this to populate the asset list and create GameObjects.
    Returns complete asset metadata including unity_object_name for scene mapping.
    
    Returns:
        List of all assets with metadata
    """
    loader = get_asset_loader()
    assets = loader.assets
    
    return {
        "total_count": len(assets),
        "assets": assets,
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "⚠️ SYNTHETIC DATA: All asset data is computer-generated for demonstration purposes."
    }


@router.get('/assets/{asset_id}')
async def get_asset_by_id(asset_id: str):
    """Get single asset by ID.
    
    Args:
        asset_id: Asset identifier (e.g., GDC-WP-007)
        
    Returns:
        Asset metadata including installation date, design specs, maintenance schedule
    """
    loader = get_asset_loader()
    asset = loader.get_asset_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset {asset_id} not found. Valid IDs: GDC-WP-001 through GDC-PP-010"
        )
    
    return {
        "asset": asset,
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "⚠️ SYNTHETIC DATA: All asset data is computer-generated for demonstration purposes."
    }


@router.get('/assets/class/{asset_class}')
async def get_assets_by_class(asset_class: str):
    """Get all assets of a specific class.
    
    Args:
        asset_class: One of WELL_PUMP, HEAT_EXCHANGER, TURBINE, PRODUCTION_PIPE
        
    Returns:
        List of assets matching the class
    """
    loader = get_asset_loader()
    all_assets = loader.assets
    
    # Filter by class (case-insensitive)
    filtered = [a for a in all_assets if a.get('asset_class', '').upper() == asset_class.upper()]
    
    if not filtered:
        valid_classes = sorted(set(a.get('asset_class', '') for a in all_assets))
        raise HTTPException(
            status_code=404,
            detail=f"No assets found for class {asset_class}. Valid classes: {', '.join(valid_classes)}"
        )
    
    return {
        "asset_class": asset_class.upper(),
        "count": len(filtered),
        "assets": filtered,
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "⚠️ SYNTHETIC DATA: All asset data is computer-generated for demonstration purposes."
    }


# Made with Bob