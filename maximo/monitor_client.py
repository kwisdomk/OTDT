"""REST API client for Maximo Monitor sensor data.

Provides HTTP bridge to Maximo MAS 9.1 Monitor module.
Build Guide Step 2: Live sensor data feed into Unity 3D model (Lines 197-205).

Supports mock mode for TechZone-independent development with deterministic
synthetic sensor data generation.

SYNTHETIC DATA DISCLAIMER: All data is computer-generated. Not representative
of any real client operational data.
"""
import logging
import os
import hashlib
import random
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Build Guide Lines 199-200: Sensor channels per asset
SENSOR_CHANNELS = [
    "temperature_c",
    "pressure_bar",
    "vibration_mm_s",
    "flow_rate_kg_s",
    "rotation_rpm"
]

# Build Guide Lines 687-699: Sensor thresholds per asset class
SENSOR_BASELINES = {
    "WELL_PUMP": {
        "temperature_c": {"normal": 285.0, "caution": 295.0, "alarm": 310.0},
        "pressure_bar": {"normal": 45.0, "caution": 50.0, "alarm": 55.0},
        "vibration_mm_s": {"normal": 2.0, "caution": 2.5, "alarm": 4.5},
        "flow_rate_kg_s": {"normal": 120.0, "caution": 100.0, "alarm": 80.0},
        "rotation_rpm": {"normal": 3600, "caution": 3800, "alarm": 4000}
    },
    "HEAT_EXCHANGER": {
        "temperature_c": {"normal": 240.0, "caution": 260.0, "alarm": 280.0},
        "pressure_bar": {"normal": 30.0, "caution": 35.0, "alarm": 40.0},
        "vibration_mm_s": {"normal": 1.5, "caution": 2.0, "alarm": 3.0},
        "flow_rate_kg_s": {"normal": 0.0, "caution": 0.0, "alarm": 0.0},  # N/A
        "rotation_rpm": {"normal": 0, "caution": 0, "alarm": 0}  # N/A
    },
    "TURBINE": {
        "temperature_c": {"normal": 215.0, "caution": 235.0, "alarm": 250.0},
        "pressure_bar": {"normal": 22.5, "caution": 27.0, "alarm": 30.0},
        "vibration_mm_s": {"normal": 1.8, "caution": 2.3, "alarm": 3.5},
        "flow_rate_kg_s": {"normal": 0.0, "caution": 0.0, "alarm": 0.0},  # N/A
        "rotation_rpm": {"normal": 3000, "caution": 3200, "alarm": 3400}
    },
    "PRODUCTION_PIPE": {
        "temperature_c": {"normal": 315.0, "caution": 330.0, "alarm": 350.0},
        "pressure_bar": {"normal": 55.0, "caution": 62.0, "alarm": 70.0},
        "vibration_mm_s": {"normal": 1.0, "caution": 1.5, "alarm": 2.5},
        "flow_rate_kg_s": {"normal": 150.0, "caution": 130.0, "alarm": 100.0},
        "rotation_rpm": {"normal": 0, "caution": 0, "alarm": 0}  # N/A
    }
}


class MaximoMonitorClient:
    """Client for Maximo Monitor REST API with mock mode support."""

    def __init__(self, base_url: str = "", username: str = "", password: str = "", mock_mode: bool = None):
        """
        Args:
            base_url: e.g. https://<your-maximo-host>/maximo (empty for mock mode)
            username: Maximo login (empty for mock mode)
            password: Maximo password (empty for mock mode)
            mock_mode: If True, generate synthetic sensor data. If None, read from env.
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.session: Optional[requests.Session] = None
        
        # Determine mock mode
        if mock_mode is None:
            mock_mode = os.getenv("MAXIMO_MOCK_MODE", "true").lower() == "true"
        
        self.mock_mode = mock_mode or not (base_url and username and password)
        
        if self.mock_mode:
            logger.info("[MOCK MODE] MaximoMonitorClient initialized in mock mode")
        else:
            logger.info("[LIVE MODE] MaximoMonitorClient initialized for real Maximo")

    def authenticate(self) -> None:
        """Establish authenticated session with Maximo."""
        if self.mock_mode:
            logger.debug("[MOCK] Skipping authentication")
            return
        
        if not self.base_url or not self.username or not self.password:
            raise ValueError("Maximo credentials required for live mode")
        
        try:
            # Basic auth for Maximo REST API
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

    def get_latest_sensors(self, asset_id: str) -> Dict[str, float]:
        """Get latest sensor readings for an asset.

        Args:
            asset_id: Maximo asset ID (e.g. GDC-WP-007)

        Returns:
            Dict with keys: temperature_c, pressure_bar, vibration_mm_s,
                            flow_rate_kg_s, rotation_rpm
        """
        if self.mock_mode:
            return self._generate_mock_sensors(asset_id)
        else:
            return self._get_real_sensors(asset_id)
    
    def _generate_mock_sensors(self, asset_id: str) -> Dict[str, float]:
        """Generate deterministic mock sensor data based on asset_id.
        
        Uses asset_id + current minute as seed for slow variation.
        Build Guide Lines 199-200: 5 sensor channels per asset.
        """
        # Extract asset class from asset_id (e.g., GDC-WP-007 -> WELL_PUMP)
        asset_class = self._infer_asset_class(asset_id)
        
        if asset_class not in SENSOR_BASELINES:
            logger.warning(f"Unknown asset class for {asset_id}, using WELL_PUMP defaults")
            asset_class = "WELL_PUMP"
        
        baselines = SENSOR_BASELINES[asset_class]
        
        # Use asset_id + current minute as seed for reproducibility
        seed_str = f"{asset_id}-{datetime.now().minute}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        sensors = {}
        for channel in SENSOR_CHANNELS:
            baseline = baselines[channel]["normal"]
            
            # Skip N/A sensors (baseline = 0)
            if baseline == 0:
                continue
            
            # Add ±5% random variation for realism
            variation = random.uniform(-0.05, 0.05)
            value = baseline * (1 + variation)
            
            # Round appropriately
            if channel == "rotation_rpm":
                sensors[channel] = int(value)
            else:
                sensors[channel] = round(value, 2)
        
        logger.debug(f"[MOCK] Generated sensors for {asset_id}: {sensors}")
        return sensors
    
    def _infer_asset_class(self, asset_id: str) -> str:
        """Infer asset class from asset_id pattern (GDC-XX-NNN)."""
        try:
            prefix = asset_id.split('-')[1]
            class_map = {
                "WP": "WELL_PUMP",
                "HX": "HEAT_EXCHANGER",
                "TU": "TURBINE",
                "PP": "PRODUCTION_PIPE"
            }
            return class_map.get(prefix, "WELL_PUMP")
        except:
            return "WELL_PUMP"
    
    def _get_real_sensors(self, asset_id: str) -> Dict[str, float]:
        """Get sensor data from real Maximo Monitor API."""
        if not self.session:
            self.authenticate()
        
        try:
            # GET from Maximo Monitor API
            response = self.session.get(
                f'{self.base_url}/oslc/os/mxasset/{asset_id}/sensors',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_maximo_sensors(data)
            else:
                logger.error(f"[LIVE] Failed to get sensors for {asset_id}: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"[LIVE] Error getting sensors for {asset_id}: {e}")
            return {}
    
    def _parse_maximo_sensors(self, data: dict) -> Dict[str, float]:
        """Parse Maximo Monitor API response to sensor dict."""
        # TODO: Implement based on actual Maximo Monitor API schema
        raise NotImplementedError("Real Maximo sensor parsing not yet implemented")

    def get_sensor_history(self, asset_id: str, hours: int = 24) -> List[Dict]:
        """Get historical sensor readings for trend analysis.

        Args:
            asset_id: Maximo asset ID
            hours: Lookback window in hours

        Returns:
            List of timestamped sensor dicts, oldest first
        """
        if self.mock_mode:
            return self._generate_mock_history(asset_id, hours)
        else:
            return self._get_real_history(asset_id, hours)
    
    def _generate_mock_history(self, asset_id: str, hours: int) -> List[Dict]:
        """Generate mock historical sensor data."""
        history = []
        now = datetime.now()
        
        for i in range(hours):
            timestamp = now - timedelta(hours=hours - i)
            
            # Generate sensors for this timestamp
            seed_str = f"{asset_id}-{timestamp.hour}"
            seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
            random.seed(seed)
            
            sensors = self._generate_mock_sensors(asset_id)
            sensors['timestamp'] = timestamp.isoformat()
            
            history.append(sensors)
        
        return history
    
    def _get_real_history(self, asset_id: str, hours: int) -> List[Dict]:
        """Get historical sensor data from real Maximo Monitor."""
        # TODO: Implement based on actual Maximo Monitor API
        raise NotImplementedError("Real Maximo history not yet implemented")

    def get_active_alerts(self) -> List[Dict]:
        """Get active alerts from Maximo Monitor.

        Returns:
            List of alert dicts with asset_id, severity, message, timestamp
        """
        if self.mock_mode:
            return self._generate_mock_alerts()
        else:
            return self._get_real_alerts()
    
    def _generate_mock_alerts(self) -> List[Dict]:
        """Generate mock alerts for demo purposes."""
        # Mock: return empty list or sample alert
        return [
            {
                "asset_id": "GDC-WP-007",
                "severity": "WARNING",
                "message": "Temperature trending upward",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    def _get_real_alerts(self) -> List[Dict]:
        """Get active alerts from real Maximo Monitor."""
        # TODO: Implement based on actual Maximo Monitor API
        raise NotImplementedError("Real Maximo alerts not yet implemented")


def main():
    """CLI entry point for testing monitor client."""
    print("=" * 60)
    print("Maximo Monitor Client Test")
    print("Build Guide Step 2: Sensor Data Bridge")
    print("=" * 60)
    print()
    
    # Initialize in mock mode
    client = MaximoMonitorClient(mock_mode=True)
    
    # Test sensor retrieval
    test_assets = ["GDC-WP-007", "GDC-HX-003", "GDC-TU-001", "GDC-PP-005"]
    
    for asset_id in test_assets:
        sensors = client.get_latest_sensors(asset_id)
        print(f"{asset_id}: {sensors}")
    
    print()
    print("[OK] Mock sensor generation working")
    print()
    print("[WARNING] SYNTHETIC DATA DISCLAIMER:")
    print("All data is computer-generated. Not representative of any")
    print("real client operational data.")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
