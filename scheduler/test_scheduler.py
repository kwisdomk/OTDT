"""Quick test for the Maintenance Scheduler (Fix 6 validation)."""
import sys, os
sys.path.insert(0, r"q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT\otdt\OTDT")

import pandas as pd
from scheduler.optimizer import MaintenanceScheduler
from monte_carlo.engine import run_simulation

# Load real GDC assets
df = pd.read_excel(r"q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT\otdt\OTDT\datasets\GDC_Assets.xlsx")
assets = df.to_dict("records")
for a in assets:
    if hasattr(a.get("last_maintenance_date", ""), "isoformat"):
        a["last_maintenance_date"] = a["last_maintenance_date"].isoformat()[:10]
    if hasattr(a.get("installation_date", ""), "isoformat"):
        a["installation_date"] = a["installation_date"].isoformat()[:10]

# Simulate MC failure probs for each asset
probs = {}
for a in assets:
    aid = a["asset_id"]
    state = {
        "bearing_temp_c": float(a.get("design_temp_c", 85)),
        "bearing_vibration_mms": 4.2,
        "steam_inlet_pressure_bar": float(a.get("design_pressure_bar", 25)),
    }
    r = run_simulation(state, n=1000)
    probs[aid] = r["failure_probability"]

# Run scheduler
sched = MaintenanceScheduler(crew_capacity=3)
result = sched.optimize_schedule(assets, probs, horizon_days=90)

# Print summary
s = result["summary"]
print(f"Scheduled: {s['total_scheduled']} tasks, Skipped: {s['total_skipped']}")
print(f"Critical: {s['critical_count']}, High: {s['high_count']}")
print(f"Maintenance cost: ${s['total_maintenance_cost_usd']:,.0f}")
print(f"Avoided failure cost: ${s['total_avoided_failure_cost_usd']:,.0f}")
print(f"Net savings: ${s['net_savings_usd']:,.0f}")
print()

# Print first 5 work orders
print("TOP 5 WORK ORDERS:")
for wo in result["work_orders"]:
    print(f"  {wo['asset_id']:15s} | {wo['scheduled_date']} | P{wo['priority_code']} | prob={wo['failure_probability']:.0%} | {wo['wo_type']}")

# Test Gantt
gantt = sched.generate_gantt(result)
print(f"\nGantt bars: {gantt['total_tasks']}")
print(f"Date range: {gantt['date_range']['start']} to {gantt['date_range']['end']}")
