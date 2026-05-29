"""
Monte Carlo simulation endpoints.
Build Guide Step 5 & 6: Failure probability and What-If analysis.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
import sys
import os

# Import Monte Carlo engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from monte_carlo.engine import run_simulation

router = APIRouter()

class MonteCarloRequest(BaseModel):
    """Request for Monte Carlo simulation."""
    asset_id: str
    sensor_state: Optional[Dict[str, float]] = None

class WhatIfRequest(BaseModel):
    """Request for What-If scenario simulation."""
    asset_id: str
    sensor_state: Optional[Dict[str, float]] = None
    maintenance_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    deferral_days: Optional[int] = None

@router.post("/simulate")
async def simulate(request: MonteCarloRequest):
    """
    Run Monte Carlo simulation to get failure probability.
    Step 5: 10,000 iterations, Weibull distributions.
    """
    result = run_simulation(request.sensor_state)
    result["asset_id"] = request.asset_id
    return result

@router.post("/whatif")
async def whatif(request: WhatIfRequest):
    """
    What-If scenario: failure probability if maintenance on given date.
    STEP 6 DEMO CALIBRATION: 0 days = 34%, 45 days = 68%
    """
    if request.deferral_days is not None:
        days_until = max(0, request.deferral_days)
    elif request.maintenance_date is not None:
        try:
            maint_date = datetime.strptime(request.maintenance_date, "%Y-%m-%d").date()
            today = date.today()
            days_until = max(0, (maint_date - today).days)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid maintenance_date format. Use YYYY-MM-DD")
    else:
        days_until = 0
    
    # DEMO CALIBRATION — Build Guide Step 6
    # 0 days = 34%, 45 days = 68%
    if days_until <= 45:
        probability = 0.34 + (days_until / 45) * (0.68 - 0.34)
    else:
        # Beyond 45 days, probability increases more slowly, capped at 95%
        probability = 0.68 + ((days_until - 45) / 135) * (1.0 - 0.68)
        probability = min(probability, 0.95)
    
    replacement_cost = 180000  # USD for well pump
    inspection_cost = 8000
    
    # Determine action based on probability
    if probability < 0.10:
        action = "MONITOR"
    elif probability < 0.25:
        action = "SCHEDULE_MAINTENANCE"
    else:
        action = "URGENT"
        
    response_date = request.maintenance_date
    if not response_date:
        response_date = (date.today() + timedelta(days=days_until)).strftime("%Y-%m-%d")
    
    return {
        "asset_id": request.asset_id,
        "deferral_days": days_until,
        "base_failure_probability": 0.34,
        "deferred_failure_probability": round(probability, 4),
        "failure_cost_usd": replacement_cost,
        "expected_failure_cost_usd": round(probability * replacement_cost, 0),
        "inspection_cost_usd": inspection_cost,
        "recommendation": action,
        "model_source": "calibrated_baseline_demo",
        
        # Preserved for backward compatibility
        "failure_probability": round(probability, 4),
        "recommended_action": action,
        "expected_cost_usd": round(probability * replacement_cost, 0),
        "maintenance_deferral_days": days_until,
        "maintenance_date": response_date,
        "synthetic": True,
        "disclaimer": "⚠️ SYNTHETIC DATA: All readings are computer-generated."
    }

@router.get("/health-check")
async def health_check():
    """Verify Monte Carlo engine is operational."""
    test_state = {
        "bearing_temp_c": 85.0,
        "bearing_vibration_mms": 4.2,
        "steam_inlet_pressure_bar": 68.0
    }
    result = run_simulation(test_state, n=100)
    return {
        "status": "healthy",
        "engine": "Weibull",
        "test_probability": result.get("failure_probability", 0),
        "synthetic": True
    }


