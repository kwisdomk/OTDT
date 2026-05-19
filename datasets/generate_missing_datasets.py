"""
Generate missing OTDT datasets:
  - Failure_History (500 records) - per Build Guide Section 4, Dataset 3
  - MC_Validation (100 records)   - per Build Guide Section 4, Dataset 4

Uses the existing GDC_Assets.xlsx to ensure asset_id consistency.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

np.random.seed(42)

# ── Load existing asset IDs ────────────────────────────────────────────────
assets_path = os.path.join(os.path.dirname(__file__), "GDC_Assets.xlsx")
assets_df = pd.read_excel(assets_path)
asset_ids = assets_df["asset_id"].tolist()
asset_classes = dict(zip(assets_df["asset_id"], assets_df["asset_class"]))
replacement_costs = dict(zip(assets_df["asset_id"], assets_df["replacement_cost_usd"]))

# ── Constants (from Build Guide) ──────────────────────────────────────────
FAILURE_MODES = [
    "BEARING_FAILURE",
    "SEAL_LEAK",
    "IMPELLER_WEAR",
    "PIPE_EROSION",
    "OVERTEMPERATURE",
    "VIBRATION_EXCESSIVE",
]

ROOT_CAUSES = [
    "Corrosion from geothermal brine",
    "Thermal cycling fatigue",
    "Vibration-induced wear",
    "Seal degradation from H2S exposure",
    "Scaling from silica deposits",
    "Foreign object damage",
    "Electrical insulation breakdown",
    "Bearing lubrication failure",
]

START_DATE = datetime(2020, 1, 1)
END_DATE   = datetime(2024, 12, 31)
TOTAL_DAYS = (END_DATE - START_DATE).days


# ══════════════════════════════════════════════════════════════════════════
#  Dataset 3: Historical Failure Events (500 records)
# ══════════════════════════════════════════════════════════════════════════
print("[GEN] Generating Failure_History (500 records)...")

failure_records = []
for i in range(500):
    asset_id = np.random.choice(asset_ids)
    failure_date = START_DATE + timedelta(days=int(np.random.uniform(0, TOTAL_DAYS)))
    failure_mode = np.random.choice(FAILURE_MODES, p=[0.25, 0.20, 0.20, 0.15, 0.12, 0.08])
    
    # Time since last maintenance (Weibull-distributed, shape=2.0, scale=120 days)
    time_since_maint = max(7, int(np.random.weibull(2.0) * 120))
    
    # Sensor warning hours (earlier warning for slower failure modes)
    if failure_mode in ("BEARING_FAILURE", "IMPELLER_WEAR"):
        warning_hours = int(np.random.uniform(24, 168))  # 1-7 days
    elif failure_mode in ("SEAL_LEAK", "PIPE_EROSION"):
        warning_hours = int(np.random.uniform(6, 72))    # 6h-3 days
    else:
        warning_hours = int(np.random.uniform(1, 24))     # 1-24 hours
    
    # Repair duration depends on failure severity
    repair_hours = int(np.random.lognormal(3.5, 0.6))  # median ~33 hours
    repair_hours = max(4, min(repair_hours, 720))       # clamp 4h-30days
    
    # Repair cost: fraction of replacement cost
    repl_cost = replacement_costs.get(asset_id, 180000)
    repair_cost = round(repl_cost * np.random.uniform(0.05, 0.35), 2)
    
    # Unplanned downtime (slightly longer than repair due to logistics)
    downtime_hours = repair_hours + int(np.random.uniform(2, 48))
    
    failure_records.append({
        "failure_id": f"GDC-FAIL-{failure_date.year}-{str(i+1).zfill(3)}",
        "asset_id": asset_id,
        "failure_date": failure_date.strftime("%Y-%m-%d %H:%M"),
        "failure_mode": failure_mode,
        "time_since_last_maintenance_days": time_since_maint,
        "sensor_warning_hours_before": warning_hours,
        "repair_duration_hours": repair_hours,
        "repair_cost_usd": repair_cost,
        "unplanned_downtime_hours": downtime_hours,
        "root_cause": np.random.choice(ROOT_CAUSES),
    })

failure_df = pd.DataFrame(failure_records)
failure_path = os.path.join(os.path.dirname(__file__), "Failure_History.xlsx")
failure_df.to_excel(failure_path, sheet_name="Failure_History", index=False)
print(f"[GEN] OK Failure_History.xlsx -- {len(failure_df)} records saved to {failure_path}")


# ══════════════════════════════════════════════════════════════════════════
#  Dataset 4: Monte Carlo Validation Cases (100 records)
# ══════════════════════════════════════════════════════════════════════════
print("[GEN] Generating MC_Validation (100 records)...")

# Use failure history to create validation cases
# For each case: pick a historical point, run "what would MC have predicted?"
validation_records = []
for i in range(100):
    asset_id = np.random.choice(asset_ids)
    sim_date = START_DATE + timedelta(days=int(np.random.uniform(30, TOTAL_DAYS - 30)))
    
    # Sensor state at simulation time (realistic ranges)
    asset_class = asset_classes.get(asset_id, "WELL_PUMP")
    if asset_class == "WELL_PUMP":
        temp = round(np.random.normal(85, 8), 1)
        vib  = round(np.random.normal(4.2, 1.5), 2)
        pres = round(np.random.normal(25, 3), 1)
    elif asset_class == "HEAT_EXCHANGER":
        temp = round(np.random.normal(95, 10), 1)
        vib  = round(np.random.normal(3.0, 1.0), 2)
        pres = round(np.random.normal(15, 2), 1)
    elif asset_class == "TURBINE":
        temp = round(np.random.normal(110, 12), 1)
        vib  = round(np.random.normal(3.5, 1.2), 2)
        pres = round(np.random.normal(68, 5), 1)
    else:  # PRODUCTION_PIPE
        temp = round(np.random.normal(75, 6), 1)
        vib  = round(np.random.normal(2.0, 0.8), 2)
        pres = round(np.random.normal(30, 4), 1)
    
    sensor_state = {
        "bearing_temp_c": max(40, temp),
        "bearing_vibration_mms": max(0.5, vib),
        "steam_inlet_pressure_bar": max(5, pres),
    }
    
    days_since_maint = int(np.random.uniform(10, 200))
    
    # Simulated failure probability (Weibull-based, correlated with sensor severity)
    severity = (temp / 105.0) * 0.4 + (vib / 7.1) * 0.4 + (pres / 85.0) * 0.2
    sim_prob = round(min(0.95, max(0.02, severity * np.random.uniform(0.6, 1.2))), 4)
    
    # Ground truth: did the asset actually fail within 30 days?
    # Higher sim_prob → higher chance of actual failure (with noise)
    actual_failure = 1 if np.random.random() < (sim_prob * 0.85 + 0.05) else 0
    
    # Confidence intervals
    ci_low  = round(max(0, sim_prob - np.random.uniform(0.08, 0.15)), 4)
    ci_high = round(min(1, sim_prob + np.random.uniform(0.08, 0.15)), 4)
    
    # Was the simulation correct?
    sim_correct = (sim_prob > 0.5 and actual_failure == 1) or (sim_prob <= 0.5 and actual_failure == 0)
    
    validation_records.append({
        "validation_id": f"MC-VAL-{str(i+1).zfill(3)}",
        "asset_id": asset_id,
        "simulation_date": sim_date.strftime("%Y-%m-%d"),
        "sensor_state_json": json.dumps(sensor_state),
        "days_since_maintenance": days_since_maint,
        "simulated_failure_prob_30d": sim_prob,
        "actual_failure_within_30d": actual_failure,
        "simulation_correct": sim_correct,
        "confidence_interval_low": ci_low,
        "confidence_interval_high": ci_high,
    })

validation_df = pd.DataFrame(validation_records)
validation_path = os.path.join(os.path.dirname(__file__), "MC_Validation.xlsx")
validation_df.to_excel(validation_path, sheet_name="MC_Validation", index=False)

accuracy = sum(1 for r in validation_records if r["simulation_correct"]) / len(validation_records)
print(f"[GEN] OK MC_Validation.xlsx -- {len(validation_df)} records, accuracy={accuracy:.1%}")
print("[GEN] Done.")
