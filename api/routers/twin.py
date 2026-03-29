"""
Digital Twin API endpoints.

Build Guide Step 2 (Lines 203-205): Unity 3D model polls these endpoints
for real-time sensor updates every 1 second.

⚠️ SYNTHETIC DATA: All readings are computer-generated.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
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


def calculate_health_score(sensors: dict, thresholds: dict) -> float:
    """Calculate health score based on sensor proximity to alarm thresholds.
    
    Build Guide: Health score 100 = perfect, 0 = critical failure.
    Decreases as sensors approach alarm thresholds.
    """
    scores = []
    for sensor, value in sensors.items():
        if sensor not in thresholds:
            continue
        t = thresholds[sensor]
        normal_max = t["caution"]
        alarm_min = t["alarm"]
        
        if value <= normal_max:
            scores.append(100.0)
        elif value >= alarm_min:
            scores.append(0.0)
        else:
            # Linear interpolation in caution range
            caution_range = alarm_min - normal_max
            distance_into_caution = value - normal_max
            scores.append(100.0 * (1 - distance_into_caution / caution_range))
    
    return round(sum(scores) / len(scores), 1) if scores else 100.0


def calculate_status(sensors: dict, thresholds: dict) -> tuple[str, str, str]:
    """Calculate status, reason, and colour code.
    
    Build Guide Lines 229-230: NORMAL (green) / CAUTION (amber) / ALARM (red)
    """
    for sensor, value in sensors.items():
        if sensor not in thresholds:
            continue
        t = thresholds[sensor]
        if value >= t["alarm"]:
            return "ALARM", f"{sensor} in alarm range", "#FF0000"
        elif value >= t["caution"]:
            return "CAUTION", f"{sensor} in caution range", "#FFA500"
    
    return "NORMAL", "All sensors within normal operating range", "#00FF00"


# Sensor thresholds per asset class (from monitor_client.py)
SENSOR_THRESHOLDS = {
    "WELL_PUMP": {
        "temperature_c": {"caution": 295.0, "alarm": 310.0},
        "pressure_bar": {"caution": 50.0, "alarm": 55.0},
        "vibration_mm_s": {"caution": 2.5, "alarm": 4.5},
    },
    "HEAT_EXCHANGER": {
        "temperature_c": {"caution": 260.0, "alarm": 280.0},
        "pressure_bar": {"caution": 35.0, "alarm": 40.0},
        "vibration_mm_s": {"caution": 2.0, "alarm": 3.0},
    },
    "TURBINE": {
        "temperature_c": {"caution": 235.0, "alarm": 250.0},
        "pressure_bar": {"caution": 27.0, "alarm": 30.0},
        "vibration_mm_s": {"caution": 2.3, "alarm": 3.5},
    },
    "PRODUCTION_PIPE": {
        "temperature_c": {"caution": 330.0, "alarm": 350.0},
        "pressure_bar": {"caution": 62.0, "alarm": 70.0},
        "vibration_mm_s": {"caution": 1.5, "alarm": 2.5},
    }
}


@router.get('/twins/{asset_id}/sensors/latest')
async def get_latest_sensors(asset_id: str):
    """Get latest sensor readings for an asset.
    
    Build Guide Step 2 (Line 203): Unity 3D model polls this endpoint every 1 second
    for real-time sensor updates. Response time must be < 500ms.
    
    Args:
        asset_id: Asset identifier (e.g., GDC-WP-007)
        
    Returns:
        Sensor readings with health score, status, and colour code for Unity
    """
    # Get asset details
    loader = get_asset_loader()
    asset = loader.get_asset_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset {asset_id} not found",
        )
    
    # Get sensor readings
    client = get_monitor_client()
    sensors = client.get_latest_sensors(asset_id)
    
    # Get thresholds for this asset class
    asset_class = asset['asset_class']
    thresholds = SENSOR_THRESHOLDS.get(asset_class, SENSOR_THRESHOLDS["WELL_PUMP"])
    
    # Use health_score from monitor_client if provided (e.g., WP-07 override)
    # Otherwise calculate from sensor thresholds
    if 'health_score' in sensors:
        health_score = sensors.pop('health_score')  # Remove from sensors dict, use separately
    else:
        health_score = calculate_health_score(sensors, thresholds)
    
    status, status_reason, colour_code = calculate_status(sensors, thresholds)
    
    return {
        "asset_id": asset_id,
        "asset_class": asset_class,
        "timestamp": datetime.now().isoformat(),
        "sensors": sensors,
        "thresholds": thresholds,
        "health_score": health_score,
        "status": status,
        "status_reason": status_reason,
        "colour_code": colour_code,
        "disclaimer": "⚠️ SYNTHETIC DATA: All readings are computer-generated."
    }


@router.get('/twins/{asset_id}/sensors/history')
async def get_sensor_history(asset_id: str, hours: int = 24):
    """Get historical sensor readings for trend analysis.
    
    Args:
        asset_id: Asset identifier
        hours: Lookback window in hours (default: 24)
        
    Returns:
        List of timestamped sensor readings
    """
    # Verify asset exists
    loader = get_asset_loader()
    asset = loader.get_asset_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset {asset_id} not found",
        )
    
    # Get historical data
    client = get_monitor_client()
    history = client.get_sensor_history(asset_id, hours)
    
    return {
        "asset_id": asset_id,
        "hours": hours,
        "data_points": len(history),
        "history": history,
        "disclaimer": "⚠️ SYNTHETIC DATA: All readings are computer-generated."
    }

# Made with Bob
