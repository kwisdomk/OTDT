"""
IBM watsonx.ai NLP Router
Natural language interface for What-If analysis using IBM watsonx.ai granite model.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging

from api.integrations.watsonx_client import get_watsonx_client

router = APIRouter()
logger = logging.getLogger(__name__)


class WatsonXQueryRequest(BaseModel):
    """Natural language query for What-If analysis."""
    query: str
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What if I defer WP-07 maintenance by 45 days?"
            }
        }


@router.post("/whatif-nlp")
async def whatif_nlp(request: WatsonXQueryRequest):
    """
    Natural language What-If analysis powered by IBM watsonx.ai.
    
    Extracts maintenance deferral parameters from natural language,
    then runs Monte Carlo simulation to calculate failure probability.
    
    Example queries:
    - "What if I defer WP-07 maintenance by 45 days?"
    - "What happens if we delay GDC-HX-003 inspection for 60 days?"
    - "Defer turbine TU-005 by 30 days"
    """
    try:
        # Step 1: Extract parameters using watsonx.ai
        client = get_watsonx_client()
        extracted = await client.query_whatif(request.query)
        
        asset_id = extracted.get("asset_id", "GDC-WP-007")
        deferral_days = extracted.get("deferral_days", 45)
        
        logger.info(f"Extracted from query: asset_id={asset_id}, deferral_days={deferral_days}")
        
        # Step 2: Calculate maintenance date
        maintenance_date = (date.today() + timedelta(days=deferral_days)).isoformat()
        
        # Step 3: Run What-If simulation via Monte Carlo engine
        from monte_carlo.engine import whatif_simulation
        mc_result = whatif_simulation({}, deferral_days)
        probability = mc_result["failure_probability"]
        
        # Step 4: Calculate expected cost
        replacement_cost = 180000  # USD for well pump (Build Guide)
        expected_cost = probability * replacement_cost
        
        # Step 5: Determine recommendation
        if probability < 0.10:
            recommendation = "MONITOR - Low risk, continue normal operations"
        elif probability < 0.25:
            recommendation = "SCHEDULE_MAINTENANCE - Moderate risk, plan inspection"
        elif probability < 0.50:
            recommendation = "URGENT - High risk, schedule maintenance immediately"
        else:
            recommendation = "CRITICAL - Very high risk, defer maintenance not recommended"
        
        # Step 6: Return combined response
        return {
            "query": request.query,
            "extracted_asset_id": asset_id,
            "extracted_deferral_days": deferral_days,
            "maintenance_date": maintenance_date,
            "failure_probability": round(probability, 4),
            "failure_probability_percent": f"{round(probability * 100, 1)}%",
            "expected_cost_usd": round(expected_cost, 0),
            "replacement_cost_usd": replacement_cost,
            "recommendation": recommendation,
            "powered_by": "IBM watsonx.ai granite-13b-chat-v2",
            "synthetic": True,
            "disclaimer": "⚠️ SYNTHETIC DATA: All readings and predictions are computer-generated for demonstration purposes."
        }
        
    except Exception as e:
        logger.error(f"watsonx.ai NLP query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process natural language query: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check watsonx.ai integration health."""
    client = get_watsonx_client()
    
    return {
        "status": "healthy",
        "service": "IBM watsonx.ai NLP",
        "model": "ibm/granite-13b-chat-v2",
        "mock_mode": client.mock_mode,
        "endpoint": "/api/watsonx/whatif-nlp",
        "example_query": "What if I defer WP-07 maintenance by 45 days?"
    }


@router.post("/extract")
async def extract_parameters(request: WatsonXQueryRequest):
    """
    Extract maintenance parameters from natural language (testing endpoint).
    
    Returns only the extracted parameters without running simulation.
    Useful for testing watsonx.ai NLP extraction.
    """
    try:
        client = get_watsonx_client()
        extracted = await client.query_whatif(request.query)
        
        return {
            "query": request.query,
            "extracted": extracted,
            "powered_by": "IBM watsonx.ai granite-13b-chat-v2",
            "mock_mode": client.mock_mode
        }
        
    except Exception as e:
        logger.error(f"Parameter extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract parameters: {str(e)}"
        )


# Example queries for documentation
EXAMPLE_QUERIES = [
    "What if I defer WP-07 maintenance by 45 days?",
    "What happens if we delay GDC-HX-003 inspection for 60 days?",
    "Defer turbine TU-005 by 30 days",
    "What if we wait 90 days for pump 12?",
    "Can we postpone heat exchanger 5 maintenance by 2 months?",
    "What's the risk if I delay WP-015 by 120 days?"
]


@router.get("/examples")
async def get_examples():
    """Get example natural language queries."""
    return {
        "service": "IBM watsonx.ai NLP for What-If Analysis",
        "examples": EXAMPLE_QUERIES,
        "usage": "POST /api/watsonx/whatif-nlp with body: {\"query\": \"<your question>\"}"
    }

# Made with Bob
