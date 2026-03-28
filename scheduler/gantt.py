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
    # TODO: Implement — map schedule entries to {id, asset_id, start, end, label}
    raise NotImplementedError


def generate_gantt_image(schedule: Dict[str, Any], output_path: str) -> None:
    """Render Gantt chart as PNG.

    Args:
        schedule: Output of MaintenanceScheduler.optimize_schedule()
        output_path: Absolute path for output PNG file
    """
    # TODO: Implement with matplotlib.patches.FancyBboxPatch + timeline
    raise NotImplementedError
