"""Generate Gantt chart output for maintenance schedule.

Build Guide Step 8: Visualises 90-day schedule as JSON + PNG.
JSON consumed by React/Recharts; PNG used in reporting PDF.
"""
import json
from typing import Dict, List, Any
from datetime import date


def generate_gantt_json(schedule: Dict[str, Any]) -> str:
    """Serialise schedule as Gantt-compatible JSON.

    Args:
        schedule: Output of MaintenanceScheduler.optimize_schedule()

    Returns:
        JSON string compatible with Recharts timeline component
    """
    from scheduler.optimizer import MaintenanceScheduler
    scheduler = MaintenanceScheduler()
    gantt_data = scheduler.generate_gantt(schedule)
    return json.dumps(gantt_data, indent=2, default=str)


def generate_gantt_image(schedule: Dict[str, Any], output_path: str) -> None:
    """Render Gantt chart as PNG using matplotlib.

    Args:
        schedule: Output of MaintenanceScheduler.optimize_schedule()
        output_path: Absolute path for output PNG file
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from datetime import datetime
    except ImportError:
        raise ImportError("matplotlib is required for Gantt chart rendering: pip install matplotlib")

    entries = schedule.get("schedule", [])
    if not entries:
        return

    # Parse dates and set up y-axis
    asset_ids = sorted(set(e["asset_id"] for e in entries))
    asset_y = {aid: i for i, aid in enumerate(asset_ids)}

    colour_map = {
        "CRITICAL": "#C00000",
        "HIGH": "#FF6600",
        "MEDIUM": "#FF9900",
        "LOW": "#1E6B3C",
    }

    fig, ax = plt.subplots(figsize=(14, max(4, len(asset_ids) * 0.4)))

    # Find date range
    all_dates = [datetime.fromisoformat(e["scheduled_date"]) for e in entries]
    min_date = min(all_dates)

    for entry in entries:
        d = datetime.fromisoformat(entry["scheduled_date"])
        x = (d - min_date).days
        y = asset_y[entry["asset_id"]]
        colour = colour_map.get(entry["priority"], "#888888")

        ax.barh(y, width=1, left=x, height=0.6, color=colour, edgecolor="white", linewidth=0.5)

    # Labels
    ax.set_yticks(range(len(asset_ids)))
    ax.set_yticklabels(asset_ids, fontsize=7)
    ax.set_xlabel("Days from schedule start")
    ax.set_title("90-Day Maintenance Schedule (Monte Carlo Optimised)", fontsize=12, fontweight="bold")

    # Legend
    legend_patches = [mpatches.Patch(color=c, label=l) for l, c in colour_map.items()]
    ax.legend(handles=legend_patches, loc="upper right", fontsize=8)

    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
