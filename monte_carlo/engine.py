# monte_carlo/engine.py
"""
Monte Carlo failure probability engine.

Runs n_iterations probabilistic scenarios over current sensor state.
Each scenario samples sensor values from their uncertainty distributions.
Failure = any sensor exceeds its critical threshold in that scenario.
Probability = failed_scenarios / total_scenarios.
"""

import numpy as np
from scipy import stats
from datetime import datetime, timedelta, date

THRESHOLDS = {
    'bearing_temp_c': 105.0,
    'bearing_vibration_mms': 7.1,
    'steam_inlet_pressure_bar': 85.0,
}
DRIFT_RATE = 0.002 * 86400  # mm/s per day


def run_simulation(sensor_state: dict, n: int = 10_000) -> dict:
    """
    Args:
        sensor_state: Philip's JSON sensors{} dict with raw float values
        n: iteration count (10000 prod, 1000 tests)

    Returns:
        dict with failure_probability, days estimates, action, optimal_maintenance_day
    """
    np.random.seed(None)

    T = stats.norm(sensor_state['bearing_temp_c'], 2.5).rvs(n)
    V = stats.norm(sensor_state['bearing_vibration_mms'], 0.4).rvs(n)
    P = stats.norm(sensor_state['steam_inlet_pressure_bar'], 1.5).rvs(n)

    fails = (T > THRESHOLDS['bearing_temp_c']) | \
            (V > THRESHOLDS['bearing_vibration_mms']) | \
            (P > THRESHOLDS['steam_inlet_pressure_bar'])

    prob = float(fails.sum() / n)

    curr_vib = sensor_state['bearing_vibration_mms']
    days_p50 = max(1, int((THRESHOLDS['bearing_vibration_mms'] - curr_vib) / DRIFT_RATE))
    days_p95 = max(1, int(days_p50 * 0.6))

    action = 'MONITOR' if prob < 0.10 else ('SCHEDULE_MAINTENANCE' if prob < 0.25 else 'URGENT')
    opt_day = (datetime.utcnow() + timedelta(days=max(1, days_p50-5))).strftime('%Y-%m-%d')

    return {
        'asset_id': sensor_state.get('asset_id', 'GDC-WP-007'),
        'failure_probability': round(prob, 4),
        'days_to_failure_p50': days_p50,
        'days_to_failure_p95': days_p95,
        'recommended_action': action,
        'optimal_maintenance_day': opt_day,
        'simulation_iterations': n,
    }


def whatif_simulation(sensor_state: dict, maintenance_date: str, n: int = 10_000) -> dict:
    """
    Simulates failure probability assuming maintenance on maintenance_date.
    Earlier maintenance → lower accumulated drift → lower probability.
    Called by FastAPI /whatif/simulate when Maurine's slider fires.
    """
    days_until = max(0, (date.fromisoformat(maintenance_date) - date.today()).days)

    # Post-maintenance: drift resets, vibration drops proportionally
    adjusted_vib = max(3.5, sensor_state['bearing_vibration_mms'] - days_until * DRIFT_RATE * 0.3)
    adjusted = {**sensor_state, 'bearing_vibration_mms': adjusted_vib}

    return run_simulation(adjusted, n)