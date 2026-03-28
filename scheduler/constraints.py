"""Constraint definitions for maintenance scheduler.

Build Guide Step 8 constraints:
- Crew availability: 3 inspections/day maximum
- Equipment interdependencies: Compressor must precede cooler maintenance
- Regulatory compliance: Safety relief valve testing quarterly
- Budget limits: Monthly maintenance spend cap
"""
from typing import List, Dict, Any


def get_crew_constraint() -> Dict[str, Any]:
    """Return crew availability constraint."""
    return {
        "type": "max_daily",
        "value": 3,
        "description": "Maximum 3 maintenance inspections per day",
    }


def get_interdependencies() -> List[Dict[str, Any]]:
    """Return equipment interdependency rules."""
    return [
        {
            "parent": "GDC-COMPRESSOR-01",
            "child": "GDC-COOLER-01",
            "type": "must_precede",
            "days_before": 7,
            "reason": "Compressor must run during cooler maintenance window",
        }
    ]


def get_regulatory_windows() -> List[Dict[str, Any]]:
    """Return regulatory compliance requirements."""
    return [
        {
            "asset_class": "PRESSURE_VESSEL",
            "requirement": "quarterly_inspection",
            "max_days_between": 90,
        },
        {
            "asset_class": "SAFETY_VALVE",
            "requirement": "annual_test",
            "max_days_between": 365,
        },
    ]


def get_budget_constraint(monthly_cap_usd: float = 50_000.0) -> Dict[str, Any]:
    """Return monthly budget cap constraint.

    Args:
        monthly_cap_usd: Maximum monthly maintenance spend.
    """
    return {
        "type": "monthly_budget",
        "value": monthly_cap_usd,
        "description": f"Monthly maintenance budget cap: USD {monthly_cap_usd:,.0f}",
    }
