"""
IBM watsonx.ai NLP Client for What-If Analysis
Extracts maintenance deferral parameters from natural language queries.
"""

import os
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Check if ibm-watsonx-ai is available
try:
    from ibm_watsonx_ai import APIClient
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False
    logger.warning("ibm-watsonx-ai not installed. Install with: pip install ibm-watsonx-ai")


class WatsonXClient:
    """Client for IBM watsonx.ai natural language query processing."""
    
    def __init__(self, mock_mode: Optional[bool] = None):
        """
        Initialize watsonx.ai client.
        
        Args:
            mock_mode: If True, return mock responses. If None, read from env.
        """
        # Read configuration from environment
        self.api_key = os.getenv('WATSONX_API_KEY', '')
        self.project_id = os.getenv('WATSONX_PROJECT_ID', '')
        self.url = os.getenv('WATSONX_URL', 'https://eu-de.ml.cloud.ibm.com')
        self.model_id = os.getenv('WATSONX_MODEL_ID', 'ibm/granite-13b-chat-v2')
        
        # Determine mock mode
        if mock_mode is None:
            mock_mode = os.getenv("WATSONX_MOCK_MODE", "true").lower() == "true"
        
        self.mock_mode = mock_mode
        self.client = None
        self.model = None
        
        if self.mock_mode:
            logger.info("[MOCK MODE] WatsonXClient initialized in mock mode")
        else:
            if not WATSONX_AVAILABLE:
                logger.error("ibm-watsonx-ai package not installed. Falling back to mock mode.")
                self.mock_mode = True
            elif not self.api_key or not self.project_id:
                logger.warning("watsonx.ai credentials not configured. Falling back to mock mode.")
                self.mock_mode = True
            else:
                self._initialize_client()
    
    def _initialize_client(self):
        """Initialize watsonx.ai API client."""
        try:
            # Create credentials
            credentials = Credentials(
                url=self.url,
                api_key=self.api_key
            )
            
            # Initialize API client
            self.client = APIClient(credentials)
            
            # Initialize model inference
            self.model = ModelInference(
                model_id=self.model_id,
                api_client=self.client,
                project_id=self.project_id
            )
            
            logger.info(f"[LIVE MODE] WatsonXClient initialized with model {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize watsonx.ai client: {e}")
            logger.warning("Falling back to mock mode")
            self.mock_mode = True
    
    async def query_whatif(self, natural_language_query: str) -> Dict:
        """
        Extract maintenance deferral parameters from natural language query.
        
        Args:
            natural_language_query: User's question about maintenance deferral
                Example: "What if I defer WP-07 maintenance by 45 days?"
        
        Returns:
            dict: {
                "deferral_days": int (0-180),
                "asset_id": str (e.g., "GDC-WP-007")
            }
        """
        if self.mock_mode:
            return self._mock_query(natural_language_query)
        
        try:
            return await self._real_query(natural_language_query)
        except Exception as e:
            logger.error(f"watsonx.ai query failed: {e}. Falling back to mock.")
            return self._mock_query(natural_language_query)
    
    def _mock_query(self, query: str) -> Dict:
        """Generate mock response for development/testing."""
        logger.info(f"[MOCK] Processing query: {query}")
        
        # Simple pattern matching for demo
        query_lower = query.lower()
        
        # Extract asset ID
        asset_id = "GDC-WP-007"  # Default
        for asset_type in ["wp", "hx", "tu", "pp"]:
            if asset_type in query_lower:
                # Try to find number after asset type
                import re
                pattern = f"{asset_type}[-\\s]?(\\d{{1,3}})"
                match = re.search(pattern, query_lower)
                if match:
                    num = match.group(1).zfill(3)
                    asset_id = f"GDC-{asset_type.upper()}-{num}"
                    break
        
        # Extract deferral days
        deferral_days = 45  # Default
        import re
        # Look for patterns like "45 days", "30 days", etc.
        day_pattern = r"(\d+)\s*days?"
        match = re.search(day_pattern, query_lower)
        if match:
            deferral_days = min(int(match.group(1)), 180)  # Cap at 180
        
        result = {
            "deferral_days": deferral_days,
            "asset_id": asset_id
        }
        
        logger.info(f"[MOCK] Extracted: {result}")
        return result
    
    async def _real_query(self, query: str) -> Dict:
        """Query watsonx.ai granite model for parameter extraction."""
        logger.info(f"[LIVE] Querying watsonx.ai: {query}")
        
        # System prompt for parameter extraction
        system_prompt = """You are a maintenance AI assistant for GDC Kenya geothermal plant.
Extract maintenance deferral parameters from user queries.

Rules:
1. Extract deferral_days (integer 0-180) from the query
2. Extract asset_id in format GDC-XX-NNN where XX is asset type (WP/HX/TU/PP)
3. Return ONLY valid JSON, no other text
4. If asset not specified, use "GDC-WP-007"
5. If days not specified, use 45

Response format:
{"deferral_days": <int>, "asset_id": "<string>"}"""
        
        # Construct prompt
        full_prompt = f"{system_prompt}\n\nUser query: {query}\n\nJSON response:"
        
        # Generate response
        response = self.model.generate(
            prompt=full_prompt,
            params={
                "max_new_tokens": 100,
                "temperature": 0.1,  # Low temperature for consistent extraction
                "top_p": 0.9,
                "top_k": 50
            }
        )
        
        # Extract generated text
        generated_text = response.get('results', [{}])[0].get('generated_text', '{}')
        
        logger.info(f"[LIVE] watsonx.ai response: {generated_text}")
        
        # Parse JSON response
        try:
            result = json.loads(generated_text.strip())
            
            # Validate and sanitize
            deferral_days = int(result.get('deferral_days', 45))
            deferral_days = max(0, min(deferral_days, 180))  # Clamp to 0-180
            
            asset_id = result.get('asset_id', 'GDC-WP-007')
            
            return {
                "deferral_days": deferral_days,
                "asset_id": asset_id
            }
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse watsonx.ai response: {e}")
            # Fallback to mock parsing
            return self._mock_query(query)


# Singleton instance
_watsonx_client: Optional[WatsonXClient] = None


def get_watsonx_client() -> WatsonXClient:
    """Get or create WatsonXClient singleton."""
    global _watsonx_client
    if _watsonx_client is None:
        _watsonx_client = WatsonXClient()
    return _watsonx_client


# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 60)
        print("IBM watsonx.ai NLP Client Test")
        print("=" * 60)
        
        client = WatsonXClient(mock_mode=True)
        
        test_queries = [
            "What if I defer WP-07 maintenance by 45 days?",
            "What happens if we delay GDC-HX-003 inspection for 60 days?",
            "Defer turbine TU-005 by 30 days",
            "What if we wait 90 days for pump 12?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            result = await client.query_whatif(query)
            print(f"Result: {result}")
    
    asyncio.run(test())

# Made with Bob
