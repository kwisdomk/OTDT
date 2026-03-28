"""
LangGraph Agent Integration API.

Provides trigger endpoint for cross-agent communication.
GridSentinel fires event → LangGraph routes to OTDT → OTDT runs Monte Carlo → returns risk assessment.

⚠️ SYNTHETIC DATA: All simulations use computer-generated sensor data.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from monte_carlo.engine import run_simulation

router = APIRouter()


class AgentTriggerRequest(BaseModel):
    """Request body for agent trigger from LangGraph."""
    source: str = Field(..., description="Source agent (e.g., 'gridsent', 'langgraph')")
    asset_id: str = Field(..., description="Asset identifier (e.g., GDC-WP-007)")
    event_type: str = Field(..., description="Event type (e.g., 'anomaly', 'threshold_breach')")
    sensor_state: Dict[str, Any] = Field(..., description="Current sensor readings")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class AgentTriggerResponse(BaseModel):
    """Response body for agent trigger."""
    asset_id: str
    failure_probability: float
    days_to_failure_p50: int
    days_to_failure_p95: int
    recommended_action: str
    optimal_maintenance_day: str
    roi_impact: Dict[str, float]
    timestamp: str
    disclaimer: str


@router.post('/agent/trigger', response_model=AgentTriggerResponse)
async def agent_trigger(request: AgentTriggerRequest):
    """Handle agent trigger event from LangGraph.
    
    Build Guide: This is the cross-agent integration endpoint for the 30 March demo.
    GridSentinel detects anomaly → LangGraph routes to OTDT → OTDT runs Monte Carlo.
    
    Demo flow:
    1. GridSentinel detects anomaly in GDC-WP-007
    2. LangGraph receives event, routes to OTDT
    3. OTDT runs Monte Carlo simulation
    4. Returns risk assessment + ROI impact
    5. LangGraph aggregates responses, presents to user
    
    Args:
        request: Event trigger with source, asset_id, event_type, sensor_state
        
    Returns:
        Risk assessment with failure probability and ROI impact
    """
    try:
        # Log incoming event
        print(f"[AGENT TRIGGER] Source: {request.source}, Asset: {request.asset_id}, Event: {request.event_type}")
        
        # Extract sensor state
        sensor_state = {
            "asset_id": request.asset_id,
            "bearing_temp_c": request.sensor_state.get("bearing_temp_c", 85.0),
            "bearing_vibration_mms": request.sensor_state.get("bearing_vibration_mms", 4.2),
            "steam_inlet_pressure_bar": request.sensor_state.get("steam_inlet_pressure_bar", 24.0),
        }
        
        # Run Monte Carlo simulation
        mc_result = run_simulation(sensor_state, n=10000)
        
        # Calculate ROI impact
        # Build Guide: Platform cost USD 48k, savings USD 360k = 650% ROI
        replacement_cost = 160000.0  # Average GDC asset replacement cost
        maintenance_cost = 12000.0   # Preventive maintenance cost
        platform_cost = 48000.0      # Annual OTDT platform cost
        
        # Expected cost without OTDT (reactive maintenance)
        reactive_cost = replacement_cost * mc_result["failure_probability"]
        
        # Expected cost with OTDT (preventive maintenance)
        preventive_cost = maintenance_cost + (platform_cost / 50)  # Amortize platform cost across 50 assets
        
        # Savings and ROI
        expected_savings = reactive_cost - preventive_cost
        roi_percentage = (expected_savings / (platform_cost / 50)) * 100 if platform_cost > 0 else 0
        
        roi_impact = {
            "reactive_cost_usd": round(reactive_cost, 2),
            "preventive_cost_usd": round(preventive_cost, 2),
            "expected_savings_usd": round(expected_savings, 2),
            "roi_percentage": round(roi_percentage, 1),
            "platform_cost_per_asset_usd": round(platform_cost / 50, 2)
        }
        
        # Build response
        response = AgentTriggerResponse(
            asset_id=request.asset_id,
            failure_probability=mc_result["failure_probability"],
            days_to_failure_p50=mc_result["days_to_failure_p50"],
            days_to_failure_p95=mc_result["days_to_failure_p95"],
            recommended_action=mc_result["recommended_action"],
            optimal_maintenance_day=mc_result["optimal_maintenance_day"],
            roi_impact=roi_impact,
            timestamp=datetime.now().isoformat(),
            disclaimer="⚠️ SYNTHETIC DATA: All simulations use computer-generated sensor data."
        )
        
        print(f"[AGENT TRIGGER] Response: {mc_result['failure_probability']:.1%} failure probability, {mc_result['recommended_action']}")
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent trigger failed: {str(e)}"
        )


@router.get('/agent/health')
async def agent_health():
    """Health check for agent integration."""
    return {
        "status": "operational",
        "agent_name": "OTDT",
        "capabilities": [
            "monte_carlo_simulation",
            "failure_prediction",
            "roi_analysis",
            "maintenance_optimization"
        ],
        "timestamp": datetime.now().isoformat()
    }


@router.post('/agent/test-trigger')
async def test_agent_trigger():
    """Test endpoint for agent integration (demo purposes).
    
    Simulates GridSentinel anomaly event for GDC-WP-007.
    """
    test_request = AgentTriggerRequest(
        source="gridsent",
        asset_id="GDC-WP-007",
        event_type="anomaly",
        sensor_state={
            "bearing_temp_c": 92.5,
            "bearing_vibration_mms": 5.8,
            "steam_inlet_pressure_bar": 26.3
        },
        metadata={
            "severity": "high",
            "confidence": 0.87,
            "test_mode": True
        }
    )
    
    return await agent_trigger(test_request)


# Made with Bob