"""Auto-create work orders in Maximo MAS 9.1.

Called by Build Guide Step 8 (Scheduler) to convert maintenance schedule
into executable work orders in Maximo (Lines 349-350).

Supports mock mode for TechZone-independent development.

SYNTHETIC DATA DISCLAIMER: All data is computer-generated. Not representative
of any real client operational data.
"""
import logging
import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MaximoWorkOrderClient:
    """Client for creating work orders in Maximo with mock mode support."""

    def __init__(self, base_url: str = "", username: str = "", password: str = "",
                 site_id: str = "GDCKENYA", mock_mode: bool = None):
        """
        Args:
            base_url: e.g. https://<your-maximo-host>/maximo (empty for mock mode)
            username: Maximo login (empty for mock mode)
            password: Maximo password (empty for mock mode)
            site_id: Maximo site identifier (default: GDCKENYA)
            mock_mode: If True, generate mock work orders. If None, read from env.
        """
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.username = username
        self.password = password
        self.site_id = site_id
        self.session: Optional[requests.Session] = None
        
        # Determine mock mode
        if mock_mode is None:
            mock_mode = os.getenv("MAXIMO_MOCK_MODE", "true").lower() == "true"
        
        self.mock_mode = mock_mode or not (base_url and username and password)
        
        if self.mock_mode:
            logger.info("[MOCK MODE] MaximoWorkOrderClient initialized in mock mode")
        else:
            logger.info("[LIVE MODE] MaximoWorkOrderClient initialized for real Maximo")

    def authenticate(self) -> None:
        """Establish authenticated session with Maximo."""
        if self.mock_mode:
            logger.debug("[MOCK] Skipping authentication")
            return
        
        if not self.base_url or not self.username or not self.password:
            raise ValueError("Maximo credentials required for live mode")
        
        try:
            import base64
            creds = base64.b64encode(f'{self.username}:{self.password}'.encode()).decode()
            headers = {
                'Authorization': f'Basic {creds}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'{self.base_url}/oslc/j_security_check',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.session = requests.Session()
                self.session.headers.update(headers)
                logger.info("[LIVE] Authenticated with Maximo")
            else:
                raise Exception(f"Authentication failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"[LIVE] Authentication error: {e}")
            raise

    def create_work_order(
        self,
        asset_id: str,
        failure_probability: float,
        scheduled_date: str,
        description: str = "",
    ) -> Dict[str, Any]:
        """Create a preventive maintenance work order.

        Args:
            asset_id: The asset requiring maintenance (e.g. GDC-WP-007)
            failure_probability: Probability of failure if maintenance deferred
            scheduled_date: ISO date string (YYYY-MM-DD) for scheduled maintenance
            description: Work order description text (auto-generated if empty)

        Returns:
            Dict with work_order_id (str), status (str), and mock flag
        """
        if not description:
            description = f"AI-GENERATED: Failure probability {failure_probability*100:.0f}%"
        
        if self.mock_mode:
            return self._create_mock_work_order(asset_id, failure_probability, scheduled_date, description)
        else:
            return self._create_real_work_order(asset_id, failure_probability, scheduled_date, description)
    
    def _create_mock_work_order(self, asset_id: str, failure_probability: float,
                                scheduled_date: str, description: str) -> Dict[str, Any]:
        """Generate mock work order for demo."""
        # Generate mock work order ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        work_order_id = f"MOCK-WO-{asset_id}-{timestamp}"
        
        # Determine priority based on failure probability
        if failure_probability > 0.50:
            priority = 1  # Critical
        elif failure_probability > 0.25:
            priority = 2  # High
        else:
            priority = 3  # Normal
        
        result = {
            "work_order_id": work_order_id,
            "status": "created",
            "asset_id": asset_id,
            "site_id": self.site_id,
            "description": description,
            "priority": priority,
            "scheduled_date": scheduled_date,
            "failure_probability": failure_probability,
            "mock": True
        }
        
        logger.info(f"[MOCK] Created work order: {work_order_id} for {asset_id} (priority {priority})")
        return result
    
    def _create_real_work_order(self, asset_id: str, failure_probability: float,
                               scheduled_date: str, description: str) -> Dict[str, Any]:
        """Create work order in real Maximo via REST API."""
        if not self.session:
            self.authenticate()
        
        # Determine priority
        if failure_probability > 0.50:
            priority = 1
        elif failure_probability > 0.25:
            priority = 2
        else:
            priority = 3
        
        payload = {
            'siteid': self.site_id,
            'assetnum': asset_id,
            'description': description,
            'wopriority': priority,
            'wotype': 'PM',  # Preventive Maintenance
            'schedstart': f'{scheduled_date}T08:00:00+03:00',  # EAT timezone
        }
        
        try:
            response = self.session.post(
                f'{self.base_url}/oslc/os/mxwo',
                json=payload,
                timeout=15
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                wo_num = data.get('wonum', 'unknown')
                logger.info(f"[LIVE] Created work order: {wo_num} for {asset_id}")
                return {
                    'work_order_id': f'WO-{wo_num}',
                    'status': 'created',
                    'asset_id': asset_id,
                    'mock': False
                }
            else:
                logger.error(f"[LIVE] Failed to create work order: {response.status_code}")
                return {
                    'error': response.status_code,
                    'detail': response.text[:200],
                    'mock': False
                }
                
        except Exception as e:
            logger.error(f"[LIVE] Error creating work order: {e}")
            return {'error': str(e), 'mock': False}

    def get_work_order_status(self, work_order_id: str) -> Dict[str, Any]:
        """Query status of an existing work order.

        Args:
            work_order_id: Maximo work order number

        Returns:
            Dict with status, assigned_tech, completion_date
        """
        if self.mock_mode:
            return self._get_mock_status(work_order_id)
        else:
            return self._get_real_status(work_order_id)
    
    def _get_mock_status(self, work_order_id: str) -> Dict[str, Any]:
        """Get mock work order status."""
        return {
            "work_order_id": work_order_id,
            "status": "APPROVED",
            "assigned_tech": "MOCK-TECH-001",
            "completion_date": None,
            "mock": True
        }
    
    def _get_real_status(self, work_order_id: str) -> Dict[str, Any]:
        """Get real work order status from Maximo."""
        if not self.session:
            self.authenticate()
        
        try:
            response = self.session.get(
                f'{self.base_url}/oslc/os/mxwo/{work_order_id}',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "work_order_id": work_order_id,
                    "status": data.get('status', 'UNKNOWN'),
                    "assigned_tech": data.get('lead', 'UNASSIGNED'),
                    "completion_date": data.get('actfinish'),
                    "mock": False
                }
            else:
                return {"error": response.status_code, "mock": False}
                
        except Exception as e:
            logger.error(f"[LIVE] Error getting work order status: {e}")
            return {"error": str(e), "mock": False}


def main():
    """CLI entry point for testing work order client."""
    print("=" * 60)
    print("Maximo Work Order Client Test")
    print("Build Guide Step 8: Maintenance Scheduler Integration")
    print("=" * 60)
    print()
    
    # Initialize in mock mode
    client = MaximoWorkOrderClient(mock_mode=True)
    
    # Test work order creation
    test_cases = [
        ("GDC-WP-007", 0.68, "2026-04-15"),
        ("GDC-HX-003", 0.34, "2026-04-20"),
        ("GDC-TU-001", 0.12, "2026-05-01"),
    ]
    
    for asset_id, prob, date in test_cases:
        result = client.create_work_order(asset_id, prob, date)
        print(f"Created: {result['work_order_id']} (Priority {result['priority']})")
    
    print()
    print("[OK] Mock work order creation working")
    print()
    print("[WARNING] SYNTHETIC DATA DISCLAIMER:")
    print("All data is computer-generated. Not representative of any")
    print("real client operational data.")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
