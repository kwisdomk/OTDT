"""
Sensor data API endpoints.

Provides historical sensor readings for trend analysis and sparklines.
Unity HUD calls these endpoints to display 24-hour trend charts.

⚠️ SYNTHETIC DATA: All sensor readings are computer-generated.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional
from maximo.monitor_client import MaximoMonitorClient
from maximo.asset_loader import AssetLoader

router = APIRouter()

# Initialize clients (singleton pattern)
_monitor_client = None
_asset_loader = None


def get_monitor_client() -> MaximoMonitorClient:
    """Get or create monitor client instance."""
    global _monitor_client
    if _monitor_client is None:
        _monitor_client = MaximoMonitorClient(mock_mode=True)
    return _monitor_client


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


@router.get('/sensors/{asset_id}/history')
async def get_sensor_history(asset_id: str, hours: int = 24):
    """Get historical sensor readings for trend analysis.
    
    Build Guide: Unity HUD sparkline displays last 24 hours of sensor data.
    This endpoint provides the time-series data for that visualization.
    
    Args:
        asset_id: Asset identifier (e.g., GDC-WP-007)
        hours: Lookback window in hours (default: 24, max: 168)
        
    Returns:
        List of timestamped sensor readings with temperature, pressure, vibration
    """
    # Validate hours parameter
    if hours < 1 or hours > 168:
        raise HTTPException(
            status_code=400,
            detail="Hours parameter must be between 1 and 168 (7 days)"
        )
    
    # Verify asset exists
    loader = get_asset_loader()
    asset = loader.get_asset_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset {asset_id} not found"
        )
    
    # Get historical data
    client = get_monitor_client()
    history = client.get_sensor_history(asset_id, hours)
    
    return {
        "asset_id": asset_id,
        "asset_class": asset.get('asset_class'),
        "hours": hours,
        "data_points": len(history),
        "history": history,
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "⚠️ SYNTHETIC DATA: All readings are computer-generated."
    }


@router.get('/sensors/{asset_id}/latest')
async def get_latest_sensors(asset_id: str):
    """Get latest sensor readings for an asset.
    
    Build Guide: Unity 3D model polls this endpoint every 1 second
    for real-time sensor updates. Response time must be < 500ms.
    
    Args:
        asset_id: Asset identifier (e.g., GDC-WP-007)
        
    Returns:
        Current sensor readings with timestamp
    """
    # Verify asset exists
    loader = get_asset_loader()
    asset = loader.get_asset_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset {asset_id} not found"
        )
    
    # Get latest sensor readings
    client = get_monitor_client()
    sensors = client.get_latest_sensors(asset_id)
    
    return {
        "asset_id": asset_id,
        "asset_class": asset.get('asset_class'),
        "timestamp": datetime.now().isoformat(),
        "sensors": sensors,
        "disclaimer": "⚠️ SYNTHETIC DATA: All readings are computer-generated."
    }


@router.get('/sensors/{asset_id}/summary')
async def get_sensor_summary(asset_id: str, hours: int = 24):
    """Get statistical summary of sensor readings over time window.
    
    Args:
        asset_id: Asset identifier
        hours: Lookback window in hours (default: 24)
        
    Returns:
        Min, max, mean, std dev for each sensor over the time window
    """
    # Verify asset exists
    loader = get_asset_loader()
    asset = loader.get_asset_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset {asset_id} not found"
        )
    
    # Get historical data
    client = get_monitor_client()
    history = client.get_sensor_history(asset_id, hours)
    
    if not history:
        return {
            "asset_id": asset_id,
            "hours": hours,
            "summary": {},
            "message": "No historical data available"
        }
    
    # Calculate statistics for each sensor
    import numpy as np
    
    sensors = ["temperature_c", "pressure_bar", "vibration_mm_s"]
    summary = {}
    
    for sensor in sensors:
        values = [reading.get(sensor, 0) for reading in history if sensor in reading]
        if values:
            summary[sensor] = {
                "min": round(float(np.min(values)), 2),
                "max": round(float(np.max(values)), 2),
                "mean": round(float(np.mean(values)), 2),
                "std": round(float(np.std(values)), 2),
                "count": len(values)
            }
    
    return {
        "asset_id": asset_id,
        "asset_class": asset.get('asset_class'),
        "hours": hours,
        "summary": summary,
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "⚠️ SYNTHETIC DATA: All readings are computer-generated."
    }


# Made with Bob