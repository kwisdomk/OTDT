import numpy as np
from datetime import datetime, timedelta, date

THRESHOLDS = {
    'bearing_temp_c': 105.0,
    'bearing_vibration_mms': 7.1,
    'steam_inlet_pressure_bar': 85.0,
}
DRIFT_RATE = 0.002 * 86400  # mm/s per day

def run_simulation(sensor_state: dict, n: int = 10_000) -> dict:
    """Mock implementation for testing."""
    vib = sensor_state.get('bearing_vibration_mms', 4.2)
    prob = min(0.8, max(0.0, (vib - 4.0) / 10.0))
    days_p50 = max(1, int((THRESHOLDS['bearing_vibration_mms'] - vib) / DRIFT_RATE))
    action = 'MONITOR' if prob < 0.10 else ('SCHEDULE_MAINTENANCE' if prob < 0.25 else 'URGENT')
    opt_day = (datetime.utcnow() + timedelta(days=max(1, days_p50-5))).strftime('%Y-%m-%d')
    return {
        'asset_id': sensor_state.get('asset_id', 'GDC-WP-007'),
        'failure_probability': round(prob, 4),
        'days_to_failure_p50': days_p50,
        'days_to_failure_p95': max(1, int(days_p50 * 0.6)),
        'recommended_action': action,
        'optimal_maintenance_day': opt_day,
        'simulation_iterations': n,
    }

def whatif_simulation(sensor_state: dict, maintenance_date: str, n: int = 10_000) -> dict:
    days_until = max(0, (date.fromisoformat(maintenance_date) - date.today()).days)
    adjusted_vib = max(3.5, sensor_state.get('bearing_vibration_mms', 4.2) - days_until * DRIFT_RATE * 0.3)
    adjusted = {**sensor_state, 'bearing_vibration_mms': adjusted_vib}
    return run_simulation(adjusted, n)
