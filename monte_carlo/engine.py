# monte_carlo/engine.py
"""
Monte Carlo failure probability engine with Weibull distributions.
Build Guide Step 5: Weibull distribution fitting using scipy.stats.weibull_min
"""

from datetime import datetime, timedelta
import numpy as np
from scipy.stats import weibull_min
import os

# Thresholds per Build Guide Step 2 (Page 6)
THRESHOLDS = {
    "bearing_temp_c": 105.0,
    "bearing_vibration_mms": 7.1,
    "steam_inlet_pressure_bar": 85.0,
}

# Weibull parameters (shape = beta, scale = eta)
# Derived from historical failure data per Build Guide Step 5.2
WEIBULL_PARAMS = {
    "temperature": {"shape": 2.0, "scale": 105.0},   # Beta=2 (wear-out), Eta=105°C
    "vibration": {"shape": 1.5, "scale": 7.1},       # Beta=1.5 (random failures)
    "pressure": {"shape": 3.0, "scale": 85.0},       # Beta=3 (accelerated wear)
}

# Drift rate: 0.002 mm/s per day × 24h = 0.048 mm/s per day
DRIFT_RATE = 0.002 * 24.0  # mm/s per day

def _safe_float(d: dict, key: str, default: float) -> float:
    """Safely extract float from dict with fallback."""
    if not isinstance(d, dict):
        return default
    v = d.get(key, default)
    try:
        return default if v is None else float(v)
    except (TypeError, ValueError):
        return default

def run_simulation(sensor_state: dict, n: int = 10_000) -> dict:
    """
    Monte Carlo failure probability simulation with Weibull distributions.
    
    Args:
        sensor_state: dict with bearing_temp_c, bearing_vibration_mms, steam_inlet_pressure_bar
        n: number of Monte Carlo iterations
    
    Returns:
        dict with failure_probability, days_to_failure_p50, recommended_action
    """
    # Extract current readings with defaults
    temp = _safe_float(sensor_state, "bearing_temp_c", 85.0)
    vib = _safe_float(sensor_state, "bearing_vibration_mms", 4.2)
    pressure = _safe_float(sensor_state, "steam_inlet_pressure_bar", 68.0)
    
    # Calculate scaling factors (higher current = higher failure probability)
    temp_scale = temp / WEIBULL_PARAMS["temperature"]["scale"]
    vib_scale = vib / WEIBULL_PARAMS["vibration"]["scale"]
    pressure_scale = pressure / WEIBULL_PARAMS["pressure"]["scale"]
    
    # Sample from Weibull distributions
    temp_samples = weibull_min.rvs(
        WEIBULL_PARAMS["temperature"]["shape"],
        scale=WEIBULL_PARAMS["temperature"]["scale"],
        size=n
    ) * temp_scale
    
    vib_samples = weibull_min.rvs(
        WEIBULL_PARAMS["vibration"]["shape"],
        scale=WEIBULL_PARAMS["vibration"]["scale"],
        size=n
    ) * vib_scale
    
    pressure_samples = weibull_min.rvs(
        WEIBULL_PARAMS["pressure"]["shape"],
        scale=WEIBULL_PARAMS["pressure"]["scale"],
        size=n
    ) * pressure_scale
    
    # Failure if any threshold exceeded
    fails = (temp_samples > THRESHOLDS["bearing_temp_c"]) | \
            (vib_samples > THRESHOLDS["bearing_vibration_mms"]) | \
            (pressure_samples > THRESHOLDS["steam_inlet_pressure_bar"])
    
    failure_probability = float(fails.sum() / n)
    
    # Calculate days to failure (P50) using drift rate
    current_vib = vib
    threshold_vib = THRESHOLDS["bearing_vibration_mms"]
    days_to_failure_p50 = max(1, int((threshold_vib - current_vib) / DRIFT_RATE))
    days_to_failure_p95 = max(1, int(days_to_failure_p50 * 0.6))
    
    # Determine recommended action
    if failure_probability < 0.10:
        action = "MONITOR"
    elif failure_probability < 0.25:
        action = "SCHEDULE_MAINTENANCE"
    else:
        action = "URGENT"
    
    # Optimal maintenance day
    optimal_day = (datetime.utcnow() + timedelta(days=max(1, days_to_failure_p50 - 5))).strftime("%Y-%m-%d")
    
    return {
        "failure_probability": round(failure_probability, 4),
        "days_to_failure_p50": days_to_failure_p50,
        "days_to_failure_p95": days_to_failure_p95,
        "recommended_action": action,
        "optimal_maintenance_day": optimal_day,
        "simulation_iterations": n,
        "synthetic": True,
        "disclaimer": "⚠️ SYNTHETIC DATA: All readings are computer-generated."
    }


def whatif_simulation(sensor_state: dict, maintenance_days: int, n: int = 10_000) -> dict:
    """
    What-If scenario: failure probability if maintenance deferred N days.

    Projects current sensor readings forward using the physics-based drift
    model, then runs the full Weibull Monte Carlo simulation on the degraded
    state.  This replaces the earlier hardcoded linear curve with an actual
    probabilistic engine call (Build Guide Step 6).

    Args:
        sensor_state: current sensor readings dict
        maintenance_days: days to defer maintenance (slider value 0–180)
        n: Monte Carlo iterations (default 10,000)

    Returns:
        dict with failure_probability, time-window breakdown, cost, action
    """
    # --- 1. Base sensor values (WP-07 demo defaults) ---
    temp_now  = _safe_float(sensor_state, "bearing_temp_c", 85.0)
    vib_now   = _safe_float(sensor_state, "bearing_vibration_mms", 4.2)
    pres_now  = _safe_float(sensor_state, "steam_inlet_pressure_bar", 68.0)

    # --- 2. Project degradation forward by maintenance_days ---
    #   Vibration drifts at DRIFT_RATE mm/s per day
    #   Temperature drifts at 2x vibration drift (correlated wear)
    #   Pressure is mostly stable (slow seal degradation: 0.01 bar/day)
    vib_projected  = vib_now  + DRIFT_RATE * maintenance_days
    temp_projected = temp_now + DRIFT_RATE * 2.0 * maintenance_days
    pres_projected = pres_now + 0.01 * maintenance_days

    # --- 3. Run full Weibull Monte Carlo on projected state ---
    projected_state = {
        "bearing_temp_c": temp_projected,
        "bearing_vibration_mms": vib_projected,
        "steam_inlet_pressure_bar": pres_projected,
    }
    mc_result = run_simulation(projected_state, n=n)
    probability = mc_result["failure_probability"]

    # --- 4. Multi-window probability breakdown (per Build Guide Step 5) ---
    #   Run smaller simulations for each time window by scaling drift
    windows = {}
    for window_days in [7, 14, 30, 60, 90]:
        frac = min(window_days / max(maintenance_days, 1), 1.0)
        w_state = {
            "bearing_temp_c": temp_now + DRIFT_RATE * 2.0 * maintenance_days * frac,
            "bearing_vibration_mms": vib_now + DRIFT_RATE * maintenance_days * frac,
            "steam_inlet_pressure_bar": pres_now + 0.01 * maintenance_days * frac,
        }
        w_result = run_simulation(w_state, n=n // 2)  # half-iterations for speed
        windows[f"{window_days}d"] = round(w_result["failure_probability"], 4)

    # --- 5. Cost quantification (Build Guide Step 6) ---
    replacement_cost = 180_000  # USD for geothermal well pump
    inspection_cost  =   8_000  # USD per inspection
    expected_failure_cost = probability * replacement_cost

    # --- 6. Confidence intervals from MC sampling ---
    #   Re-sample to get percentile bounds
    temp_scale = temp_projected / WEIBULL_PARAMS["temperature"]["scale"]
    vib_scale  = vib_projected  / WEIBULL_PARAMS["vibration"]["scale"]

    vib_samples = weibull_min.rvs(
        WEIBULL_PARAMS["vibration"]["shape"],
        scale=WEIBULL_PARAMS["vibration"]["scale"],
        size=n,
    ) * vib_scale
    fail_fractions = (vib_samples > THRESHOLDS["bearing_vibration_mms"]).astype(float)
    ci_low  = float(np.percentile(fail_fractions, 5))
    ci_high = float(np.percentile(fail_fractions, 95))

    # --- 7. Action recommendation ---
    if probability < 0.10:
        action = "MONITOR"
    elif probability < 0.25:
        action = "SCHEDULE_MAINTENANCE"
    else:
        action = "URGENT"

    return {
        "failure_probability": round(probability, 4),
        "failure_probability_windows": windows,
        "confidence_interval": {"p5": round(ci_low, 4), "p95": round(ci_high, 4)},
        "recommended_action": action,
        "expected_cost_usd": round(expected_failure_cost, 0),
        "inspection_cost_usd": inspection_cost,
        "roi_ratio": round(expected_failure_cost / inspection_cost, 1) if inspection_cost else None,
        "maintenance_deferral_days": maintenance_days,
        "projected_sensors": projected_state,
        "simulation_iterations": n,
        "optimal_maintenance_day": mc_result.get("optimal_maintenance_day"),
        "synthetic": True,
        "disclaimer": "⚠️ SYNTHETIC DATA: All readings are computer-generated.",
    }


# Made with Bob
