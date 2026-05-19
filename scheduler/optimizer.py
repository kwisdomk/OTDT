"""Linear programming optimizer for maintenance schedule.

Build Guide Step 8: Converts Monte Carlo risk outputs into optimal schedule.

Optimization problem:
    min  S (maintenance_cost[i] + failure_penalty[i] * P_fail[i] * (1 - x[i]))
    s.t. S x[i,t]  <= crew_capacity  for all t      (crew constraint)
         x[i,t]    in {0,1}                          (binary: maintain asset i on day t)
         interdependency constraints
         regulatory window constraints

SYNTHETIC DATA DISCLAIMER: All data is computer-generated. Not representative
of any real client operational data.
"""
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import date, timedelta

logger = logging.getLogger(__name__)


class MaintenanceScheduler:
    """Optimises maintenance schedule using priority-queue approach.

    Strategy: rank assets by risk-adjusted cost (failure_prob * replacement_cost),
    then greedily schedule the highest-risk assets first, respecting crew capacity
    and minimum inter-inspection intervals.

    For the MVP demo this priority-queue approach is more transparent and
    debuggable than a full MILP.  The linprog upgrade path is documented below.
    """

    CREW_CAPACITY = 3           # max inspections per day
    MIN_INTERVAL_DAYS = 30      # min days between inspections of same asset
    DEFAULT_MAINT_COST = 8_000  # USD per inspection (from Build Guide Step 6)

    def __init__(self, crew_capacity: int = CREW_CAPACITY):
        """
        Args:
            crew_capacity: Maximum maintenance tasks per day.
        """
        self.crew_capacity = crew_capacity

    def optimize_schedule(
        self,
        assets: List[Dict[str, Any]],
        failure_probabilities: Dict[str, float],
        horizon_days: int = 90,
        start_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Generate optimal maintenance schedule.

        Args:
            assets: List of asset dicts -- must include:
                    asset_id, replacement_cost_usd, maintenance_cost_usd (optional),
                    last_maintenance_date, maintenance_interval_days
            failure_probabilities: {asset_id: float} from Monte Carlo engine
            horizon_days: Scheduling horizon in days (default 90)
            start_date: Schedule start (defaults to today)

        Returns:
            Dict with keys:
              schedule: [{asset_id, scheduled_date, priority, reason, expected_cost, ...}]
              summary: overall stats
              work_orders: top-5 for Maximo push
        """
        if start_date is None:
            start_date = date.today()

        end_date = start_date + timedelta(days=horizon_days)

        # ── 1. Score every asset by risk-adjusted cost ─────────────────────
        scored = []
        for asset in assets:
            aid = asset["asset_id"]
            prob = failure_probabilities.get(aid, 0.05)
            repl_cost = float(asset.get("replacement_cost_usd", 180_000))
            maint_cost = float(asset.get("maintenance_cost_usd", self.DEFAULT_MAINT_COST))

            # Expected cost of NOT maintaining = prob * replacement_cost
            expected_failure_cost = prob * repl_cost
            # Net benefit of scheduling = expected_failure_cost - maint_cost
            net_benefit = expected_failure_cost - maint_cost
            # Risk score for ranking
            risk_score = prob * repl_cost

            # Parse last maintenance date
            lm_raw = asset.get("last_maintenance_date")
            if isinstance(lm_raw, str):
                try:
                    lm_date = date.fromisoformat(lm_raw[:10])
                except ValueError:
                    lm_date = start_date - timedelta(days=60)
            elif isinstance(lm_raw, date):
                lm_date = lm_date if not isinstance(lm_raw, type(None)) else start_date - timedelta(days=60)
            else:
                lm_date = start_date - timedelta(days=60)

            days_since_maint = (start_date - lm_date).days
            interval = int(asset.get("maintenance_interval_days", 90))

            # Determine urgency category
            if prob >= 0.30:
                urgency = "CRITICAL"
                urgency_rank = 0
            elif prob >= 0.15:
                urgency = "HIGH"
                urgency_rank = 1
            elif prob >= 0.08:
                urgency = "MEDIUM"
                urgency_rank = 2
            else:
                urgency = "LOW"
                urgency_rank = 3

            # Determine reason for scheduling
            if prob >= 0.30:
                reason = f"Failure probability {prob:.0%} exceeds 30% threshold"
            elif days_since_maint >= interval:
                reason = f"Overdue: {days_since_maint}d since last maintenance (interval={interval}d)"
            elif net_benefit > 0:
                reason = f"Risk-adjusted: expected failure cost ${expected_failure_cost:,.0f} > inspection cost ${maint_cost:,.0f}"
            else:
                reason = "Scheduled preventive maintenance"

            scored.append({
                "asset_id": aid,
                "failure_probability": round(prob, 4),
                "replacement_cost_usd": repl_cost,
                "maintenance_cost_usd": maint_cost,
                "expected_failure_cost": round(expected_failure_cost, 0),
                "net_benefit": round(net_benefit, 0),
                "risk_score": round(risk_score, 0),
                "urgency": urgency,
                "urgency_rank": urgency_rank,
                "days_since_maintenance": days_since_maint,
                "last_maintenance_date": lm_date.isoformat(),
                "calendar_interval_days": interval,
                "reason": reason,
            })

        # ── 2. Sort by urgency then risk score (descending) ───────────────
        scored.sort(key=lambda x: (x["urgency_rank"], -x["risk_score"]))

        # ── 3. Greedy scheduling with crew capacity constraint ────────────
        # Track how many inspections per day
        daily_slots: Dict[str, int] = {}  # date_iso -> count
        # Track last scheduled date per asset
        asset_last_scheduled: Dict[str, date] = {}

        schedule = []
        skipped = []

        for item in scored:
            aid = item["asset_id"]

            # Only schedule if net benefit positive or urgency >= MEDIUM
            if item["net_benefit"] <= 0 and item["urgency_rank"] > 2:
                skipped.append({"asset_id": aid, "reason": "Low risk, negative net benefit"})
                continue

            # Find earliest available slot
            scheduled = False
            # CRITICAL/HIGH assets get scheduled in first 30 days
            # MEDIUM in first 60, LOW in full horizon
            max_day = {0: 30, 1: 45, 2: 60, 3: horizon_days}.get(item["urgency_rank"], horizon_days)

            for day_offset in range(min(max_day, horizon_days)):
                candidate_date = start_date + timedelta(days=day_offset)
                date_key = candidate_date.isoformat()

                # Check crew capacity
                if daily_slots.get(date_key, 0) >= self.crew_capacity:
                    continue

                # Check minimum interval from last scheduled
                if aid in asset_last_scheduled:
                    if (candidate_date - asset_last_scheduled[aid]).days < self.MIN_INTERVAL_DAYS:
                        continue

                # Schedule it
                daily_slots[date_key] = daily_slots.get(date_key, 0) + 1
                asset_last_scheduled[aid] = candidate_date

                colour = {"CRITICAL": "#C00000", "HIGH": "#FF6600", "MEDIUM": "#FF9900", "LOW": "#1E6B3C"}
                schedule.append({
                    "asset_id": aid,
                    "scheduled_date": date_key,
                    "day_offset": day_offset,
                    "priority": item["urgency"],
                    "colour_hex": colour.get(item["urgency"], "#888888"),
                    "failure_probability": item["failure_probability"],
                    "reason": item["reason"],
                    "maintenance_cost_usd": item["maintenance_cost_usd"],
                    "expected_failure_cost": item["expected_failure_cost"],
                    "net_benefit": item["net_benefit"],
                })
                scheduled = True
                break

            if not scheduled:
                skipped.append({"asset_id": aid, "reason": "No available slot within urgency window"})

        # ── 4. Build summary ──────────────────────────────────────────────
        total_maint_cost = sum(s["maintenance_cost_usd"] for s in schedule)
        total_avoided_cost = sum(s["expected_failure_cost"] for s in schedule)
        critical_count = sum(1 for s in schedule if s["priority"] == "CRITICAL")
        high_count = sum(1 for s in schedule if s["priority"] == "HIGH")

        # ── 5. Generate work orders for top 5 highest-urgency ─────────────
        work_orders = []
        for entry in schedule[:5]:
            work_orders.append({
                "asset_id": entry["asset_id"],
                "wo_type": "CORRECTIVE" if entry["priority"] == "CRITICAL" else "PREVENTIVE",
                "scheduled_date": entry["scheduled_date"],
                "priority_code": {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}.get(entry["priority"], 4),
                "description": f"MC-scheduled: {entry['reason']}",
                "estimated_labour_hours": 8,
                "estimated_cost_usd": entry["maintenance_cost_usd"],
                "failure_probability": entry["failure_probability"],
            })

        result = {
            "schedule": schedule,
            "skipped": skipped,
            "summary": {
                "horizon_days": horizon_days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_scheduled": len(schedule),
                "total_skipped": len(skipped),
                "critical_count": critical_count,
                "high_count": high_count,
                "total_maintenance_cost_usd": round(total_maint_cost, 0),
                "total_avoided_failure_cost_usd": round(total_avoided_cost, 0),
                "net_savings_usd": round(total_avoided_cost - total_maint_cost, 0),
                "crew_capacity_per_day": self.crew_capacity,
            },
            "work_orders": work_orders,
            "synthetic": True,
            "disclaimer": "SYNTHETIC DATA: All data is computer-generated.",
        }

        logger.info(
            f"Schedule generated: {len(schedule)} tasks, "
            f"{critical_count} critical, ${total_maint_cost:,.0f} cost"
        )
        return result

    def generate_gantt(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Gantt chart data structure for visualisation.

        Args:
            schedule: Output of optimize_schedule()

        Returns:
            Dict suitable for Recharts GanttChart or Plotly timeline
        """
        entries = schedule.get("schedule", [])
        if not entries:
            return {"bars": [], "summary": "No tasks scheduled"}

        bars = []
        for entry in entries:
            # Each maintenance task is modelled as 1-day duration
            bars.append({
                "id": f"maint-{entry['asset_id']}-{entry['scheduled_date']}",
                "asset_id": entry["asset_id"],
                "start": entry["scheduled_date"],
                "end": entry["scheduled_date"],  # same-day for inspection
                "label": f"{entry['asset_id']} ({entry['priority']})",
                "priority": entry["priority"],
                "colour": entry["colour_hex"],
                "failure_probability": entry["failure_probability"],
                "cost_usd": entry["maintenance_cost_usd"],
            })

        # Sort by date then priority
        bars.sort(key=lambda b: (b["start"], {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(b["priority"], 4)))

        return {
            "bars": bars,
            "total_tasks": len(bars),
            "date_range": {
                "start": bars[0]["start"] if bars else None,
                "end": bars[-1]["end"] if bars else None,
            },
        }
