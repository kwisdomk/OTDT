"""
config.py — OT Digital Twin Sensor Configuration
GDC Kenya Geothermal Assets: 50 total
  - 20 Well Pumps (WP-01 to WP-20)
  - 10 Heat Exchangers (HX-01 to HX-10)
  - 10 Turbines (TB-01 to TB-10)
  - 10 Production Pipes (PP-01 to PP-10)
 
Primary demo asset: WP-07 (GDC-WP-007)
Author: Wisdom Kinoti / i3 Technologies
"""
 
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
 
 
@dataclass
class SensorRange:
    """Normal operating range for a single sensor parameter."""
    min_val: float
    normal_min: float
    normal_max: float
    max_val: float
    unit: str
    warn_threshold: float   # fraction of max — triggers WARN
    crit_threshold: float   # fraction of max — triggers CRITICAL
 
 
@dataclass
class AssetConfig:
    """Configuration for a single physical asset."""
    asset_id: str           # e.g. "WP-07"
    gdc_id: str             # e.g. "GDC-WP-007"
    asset_type: str         # well_pump | heat_exchanger | turbine | pipe
    location: str           # e.g. "Olkaria IV, Pad 3"
    criticality: str        # high | medium | low
    sensors: Dict[str, SensorRange] = field(default_factory=dict)
    weibull_k: float = 2.5          # shape — failure rate increasing over time
    weibull_lambda_hr: float = 720.0  # scale — characteristic life in hours
 
 
# ── Sensor range templates per asset type ────────────────────────────────────
 
WELL_PUMP_SENSORS: Dict[str, SensorRange] = {
    "temperature_c": SensorRange(
        min_val=140.0, normal_min=160.0, normal_max=200.0, max_val=230.0,
        unit="°C", warn_threshold=0.88, crit_threshold=0.96
    ),
    "pressure_bar": SensorRange(
        min_val=15.0, normal_min=20.0, normal_max=30.0, max_val=38.0,
        unit="bar", warn_threshold=0.84, crit_threshold=0.94
    ),
    "vibration_mms": SensorRange(
        min_val=0.0, normal_min=1.0, normal_max=6.0, max_val=15.0,
        unit="mm/s", warn_threshold=0.60, crit_threshold=0.80
    ),
    "flow_rate_ls": SensorRange(
        min_val=40.0, normal_min=55.0, normal_max=110.0, max_val=130.0,
        unit="L/s", warn_threshold=0.40, crit_threshold=0.25  # low-flow alert
    ),
}
 
HEAT_EXCHANGER_SENSORS: Dict[str, SensorRange] = {
    "temperature_c": SensorRange(
        min_val=80.0, normal_min=100.0, normal_max=160.0, max_val=190.0,
        unit="°C", warn_threshold=0.88, crit_threshold=0.95
    ),
    "pressure_bar": SensorRange(
        min_val=8.0, normal_min=12.0, normal_max=22.0, max_val=28.0,
        unit="bar", warn_threshold=0.82, crit_threshold=0.93
    ),
    "vibration_mms": SensorRange(
        min_val=0.0, normal_min=0.5, normal_max=4.0, max_val=10.0,
        unit="mm/s", warn_threshold=0.55, crit_threshold=0.75
    ),
    "flow_rate_ls": SensorRange(
        min_val=20.0, normal_min=30.0, normal_max=70.0, max_val=90.0,
        unit="L/s", warn_threshold=0.38, crit_threshold=0.24
    ),
}
 
TURBINE_SENSORS: Dict[str, SensorRange] = {
    "temperature_c": SensorRange(
        min_val=120.0, normal_min=150.0, normal_max=200.0, max_val=240.0,
        unit="°C", warn_threshold=0.87, crit_threshold=0.95
    ),
    "pressure_bar": SensorRange(
        min_val=10.0, normal_min=16.0, normal_max=28.0, max_val=35.0,
        unit="bar", warn_threshold=0.85, crit_threshold=0.94
    ),
    "vibration_mms": SensorRange(
        min_val=0.0, normal_min=1.5, normal_max=7.0, max_val=18.0,
        unit="mm/s", warn_threshold=0.58, crit_threshold=0.78
    ),
    "flow_rate_ls": SensorRange(
        min_val=50.0, normal_min=70.0, normal_max=130.0, max_val=160.0,
        unit="L/s", warn_threshold=0.42, crit_threshold=0.26
    ),
}
 
PIPE_SENSORS: Dict[str, SensorRange] = {
    "temperature_c": SensorRange(
        min_val=100.0, normal_min=130.0, normal_max=180.0, max_val=210.0,
        unit="°C", warn_threshold=0.88, crit_threshold=0.95
    ),
    "pressure_bar": SensorRange(
        min_val=12.0, normal_min=18.0, normal_max=26.0, max_val=32.0,
        unit="bar", warn_threshold=0.83, crit_threshold=0.93
    ),
    "vibration_mms": SensorRange(
        min_val=0.0, normal_min=0.5, normal_max=3.5, max_val=8.0,
        unit="mm/s", warn_threshold=0.56, crit_threshold=0.76
    ),
    "flow_rate_ls": SensorRange(
        min_val=30.0, normal_min=45.0, normal_max=90.0, max_val=110.0,
        unit="L/s", warn_threshold=0.40, crit_threshold=0.25
    ),
}
 
_SENSOR_TEMPLATES = {
    "well_pump": WELL_PUMP_SENSORS,
    "heat_exchanger": HEAT_EXCHANGER_SENSORS,
    "turbine": TURBINE_SENSORS,
    "pipe": PIPE_SENSORS,
}
 
# ── Asset registry ────────────────────────────────────────────────────────────
 
def _build_assets() -> Dict[str, AssetConfig]:
    assets: Dict[str, AssetConfig] = {}
 
    # Well Pumps — WP-01 to WP-20
    locations_wp = [
        "Olkaria I, Pad 1", "Olkaria I, Pad 2", "Olkaria II, Pad 1",
        "Olkaria II, Pad 2", "Olkaria III, Pad 1", "Olkaria III, Pad 2",
        "Olkaria IV, Pad 1", "Olkaria IV, Pad 2", "Olkaria IV, Pad 3",
        "Olkaria IV, Pad 4", "Olkaria V, Pad 1", "Olkaria V, Pad 2",
        "Olkaria V, Pad 3", "Olkaria V, Pad 4", "Olkaria VI, Pad 1",
        "Olkaria VI, Pad 2", "Olkaria VI, Pad 3", "Olkaria VI, Pad 4",
        "Olkaria VI, Pad 5", "Olkaria VI, Pad 6",
    ]
    for i in range(1, 21):
        aid = f"WP-{i:02d}"
        assets[aid] = AssetConfig(
            asset_id=aid,
            gdc_id=f"GDC-WP-{i:03d}",
            asset_type="well_pump",
            location=locations_wp[i - 1],
            criticality="high",
            sensors=WELL_PUMP_SENSORS.copy(),
            weibull_k=2.5,
            weibull_lambda_hr=720.0,
        )
 
    # Heat Exchangers — HX-01 to HX-10
    for i in range(1, 11):
        aid = f"HX-{i:02d}"
        assets[aid] = AssetConfig(
            asset_id=aid,
            gdc_id=f"GDC-HX-{i:03d}",
            asset_type="heat_exchanger",
            location=f"Olkaria {'I' * ((i - 1) // 3 + 1)}, Station {i}",
            criticality="medium",
            sensors=HEAT_EXCHANGER_SENSORS.copy(),
            weibull_k=2.2,
            weibull_lambda_hr=960.0,
        )
 
    # Turbines — TB-01 to TB-10
    for i in range(1, 11):
        aid = f"TB-{i:02d}"
        assets[aid] = AssetConfig(
            asset_id=aid,
            gdc_id=f"GDC-TB-{i:03d}",
            asset_type="turbine",
            location=f"Olkaria {'I' * ((i - 1) // 3 + 1)}, Turbine Hall {i}",
            criticality="high",
            sensors=TURBINE_SENSORS.copy(),
            weibull_k=3.0,
            weibull_lambda_hr=1440.0,
        )
 
    # Production Pipes — PP-01 to PP-10
    for i in range(1, 11):
        aid = f"PP-{i:02d}"
        assets[aid] = AssetConfig(
            asset_id=aid,
            gdc_id=f"GDC-PP-{i:03d}",
            asset_type="pipe",
            location=f"Olkaria {'I' * ((i - 1) // 3 + 1)}, Pipeline {i}",
            criticality="medium",
            sensors=PIPE_SENSORS.copy(),
            weibull_k=2.0,
            weibull_lambda_hr=2160.0,
        )
 
    return assets
 
 
# ── Public API ────────────────────────────────────────────────────────────────
 
ASSETS: Dict[str, AssetConfig] = _build_assets()
 
DEMO_ASSET_ID = "WP-07"
DEMO_ASSET: AssetConfig = ASSETS[DEMO_ASSET_ID]
 
KAFKA_TOPIC_TELEMETRY = "sensor.telemetry"
KAFKA_TOPIC_ANOMALIES = "anomaly.alerts"
TELEMETRY_INTERVAL_S = 1.0   # publish rate
 
# Fault signatures for anomaly_injector
FAULT_SIGNATURES = {
    "bearing_wear": {
        "description": "Progressive bearing degradation — vibration spike",
        "sensor": "vibration_mms",
        "multiplier": 4.5,
        "ramp_steps": 15,
    },
    "cavitation": {
        "description": "Pump cavitation — pressure oscillation + flow drop",
        "sensor": "pressure_bar",
        "multiplier": 0.55,
        "ramp_steps": 10,
    },
    "seal_leak": {
        "description": "Mechanical seal failure — flow rate collapse",
        "sensor": "flow_rate_ls",
        "multiplier": 0.35,
        "ramp_steps": 20,
    },
    "overheating": {
        "description": "Cooling failure — temperature runaway",
        "sensor": "temperature_c",
        "multiplier": 1.18,
        "ramp_steps": 25,
    },
}
 
 
def get_asset(asset_id: str) -> AssetConfig:
    """Retrieve asset config by ID. Raises KeyError if not found."""
    if asset_id not in ASSETS:
        raise KeyError(f"Unknown asset '{asset_id}'. Valid IDs: {sorted(ASSETS.keys())}")
    return ASSETS[asset_id]
 
 
def list_assets_by_type(asset_type: str) -> List[AssetConfig]:
    """Return all assets of a given type."""
    return [a for a in ASSETS.values() if a.asset_type == asset_type]
 
 
if __name__ == "__main__":
    print(f"Total assets: {len(ASSETS)}")
    for atype in ["well_pump", "heat_exchanger", "turbine", "pipe"]:
        group = list_assets_by_type(atype)
        print(f"  {atype}: {len(group)} assets")
    print(f"\nDemo asset: {DEMO_ASSET.asset_id} ({DEMO_ASSET.gdc_id})")
    print(f"  Location: {DEMO_ASSET.location}")
    print(f"  Criticality: {DEMO_ASSET.criticality}")
    print(f"  Weibull k={DEMO_ASSET.weibull_k}, λ={DEMO_ASSET.weibull_lambda_hr}hr")
    print(f"  Sensors: {list(DEMO_ASSET.sensors.keys())}")