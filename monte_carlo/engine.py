# monte_carlo/engine.py
"""
Monte Carlo failure probability engine.

Runs n_iterations probabilistic scenarios over current sensor state.
Each scenario samples sensor values from their uncertainty distributions.
Failure = any sensor exceeds its critical threshold in that scenario.
Probability = failed_scenarios / total_scenarios.
"""

from datetime import datetime, timedelta, date
import numpy as np
from scipy import stats

THRESHOLDS = {
    "bearing_temp_c": 105.0,
    "bearing_vibration_mms": 7.1,
    "steam_inlet_pressure_bar": 85.0,
}

def _safe_float(d: dict, key: str, default: float) -> float:
    if not isinstance(d, dict):
        return default
    v = d.get(key, default)
    try:
        return default if v is None else float(v)
    except (TypeError, ValueError):
        return default


# FIX: your expected drift magnitude is ~0.05.
# The prior code multiplied by 86400, producing 172.8.
# Using 0.002 * 24 yields ~0.048.
DRIFT_RATE = 0.002 * 24.0  # bearing vibration drift per day (mm/s per day)

def run_simulation(sensor_state: dict, n: int = 10_000) -> dict:
    """
    Args:
        sensor_state: dict containing bearing_temp_c, bearing_vibration_mms, steam_inlet_pressure_bar
        n: iteration count
    """
    if not isinstance(sensor_state, dict):
        sensor_state = {}

    bearing_temp_c = _safe_float(sensor_state, "bearing_temp_c", 85.0)
    bearing_vibration_mms = _safe_float(sensor_state, "bearing_vibration_mms", 4.2)
    steam_inlet_pressure_bar = _safe_float(sensor_state, "steam_inlet_pressure_bar", 24.0)

    np.random.seed(None)

    # Sample sensor values
    T = stats.norm(bearing_temp_c, 2.5).rvs(n)
    V = stats.norm(bearing_vibration_mms, 0.4).rvs(n)
    P = stats.norm(steam_inlet_pressure_bar, 1.5).rvs(n)

    # Failure if ANY critical threshold is exceeded
    fails = (T > THRESHOLDS["bearing_temp_c"]) | (V > THRESHOLDS["bearing_vibration_mms"]) | (P > THRESHOLDS["steam_inlet_pressure_bar"])
    prob = float(fails.sum() / n)

    curr_vib = bearing_vibration_mms
    if DRIFT_RATE > 0:
        days_p50 = max(1, int((THRESHOLDS["bearing_vibration_mms"] - curr_vib) / DRIFT_RATE))
    else:
        days_p50 = 1
    days_p95 = max(1, int(days_p50 * 0.6))

    action = "MONITOR" if prob < 0.10 else ("SCHEDULE_MAINTENANCE" if prob < 0.25 else "URGENT")
    opt_day = (datetime.utcnow() + timedelta(days=max(1, days_p50 - 5))).strftime("%Y-%m-%d")

    return {
        "asset_id": sensor_state.get("asset_id") or "UNKNOWN",
        "failure_probability": round(prob, 4),
        "days_to_failure_p50": days_p50,
        "days_to_failure_p95": days_p95,
        "recommended_action": action,
        "optimal_maintenance_day": opt_day,
        "simulation_iterations": int(n),
    }


def whatif_simulation(sensor_state: dict, maintenance_date: str, n: int = 10_000) -> dict:
    """
    Simulate failure probability assuming maintenance happens on maintenance_date.

    Semantics fix:
    - Later maintenance date => more drift accumulates before maintenance => higher projected risk.
    - Apply drift to both vibration and temperature (temperature drifts ~2x per simulator).
    """
    if not isinstance(sensor_state, dict):
        sensor_state = {}

    bearing_temp_c = _safe_float(sensor_state, "bearing_temp_c", 85.0)
    bearing_vibration_mms = _safe_float(sensor_state, "bearing_vibration_mms", 4.2)
    steam_inlet_pressure_bar = _safe_float(sensor_state, "steam_inlet_pressure_bar", 24.0)

    try:
        target = date.fromisoformat(str(maintenance_date))
        days_until = max(0, (target - date.today()).days)
    except Exception:
        days_until = 0

    drift_delta = days_until * DRIFT_RATE

    # Project state at the maintenance date (pre-maintenance degradation)
    adjusted_vib = max(3.5, bearing_vibration_mms + drift_delta)
    adjusted_temp = max(0.0, bearing_temp_c + (2.0 * drift_delta))

    adjusted = {
        **sensor_state,
        "bearing_temp_c": adjusted_temp,
        "bearing_vibration_mms": adjusted_vib,
        "steam_inlet_pressure_bar": steam_inlet_pressure_bar,
    }

    return run_simulation(adjusted, n=n)