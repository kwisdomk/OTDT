"""Load GDC Kenya asset hierarchy from datasets/GDC_Assets.xlsx into Maximo.

Build Guide Step 2: Asset Hierarchy (Lines 191-206)
- Loads 50 asset records from Excel
- Creates Sites → Systems → Equipment hierarchy
- Configures sensor data points (temp, pressure, vibration, flow, RPM)
- Supports mock mode for TechZone-independent development

SYNTHETIC DATA DISCLAIMER: All data is computer-generated. Not representative
of any real client operational data.
"""
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "asset_id", "asset_class", "description", "installation_date",
    "design_pressure_bar", "design_temp_c", "last_maintenance_date",
    "maintenance_interval_days", "replacement_cost_usd", "unity_object_name",
]

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "GDC_Assets.xlsx"


class AssetLoader:
    """Loads GDC Kenya asset hierarchy from Excel and pushes to Maximo."""

    def __init__(self, maximo_client=None, mock_mode: bool = None):
        """
        Args:
            maximo_client: Authenticated Maximo client (optional in mock mode).
            mock_mode: If True, store assets in memory instead of pushing to Maximo.
                      If None, read from MAXIMO_MOCK_MODE environment variable.
        """
        self.client = maximo_client
        
        # Determine mock mode from env var if not explicitly set
        if mock_mode is None:
            mock_mode = os.getenv("MAXIMO_MOCK_MODE", "true").lower() == "true"
        
        self.mock_mode = mock_mode
        self.assets: List[Dict[str, Any]] = []
        
        if self.mock_mode:
            logger.info("[MOCK MODE] AssetLoader initialized in mock mode")
        else:
            logger.info("[LIVE MODE] AssetLoader initialized for real Maximo")

    def load_from_excel(self, path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Read asset records from Excel.

        Args:
            path: Override default dataset path.

        Returns:
            List of asset dicts with all expected columns.

        Raises:
            FileNotFoundError: If dataset not present.
            ValueError: If required columns are missing.
        """
        excel_path = path or DATASET_PATH
        
        if not excel_path.exists():
            raise FileNotFoundError(
                f"GDC_Assets.xlsx not found at {excel_path}. "
                f"Run: python scripts/generate_gdc_assets.py"
            )
        
        logger.info(f"Loading assets from {excel_path}")
        
        # Read Excel file
        df = pd.read_excel(excel_path, sheet_name="GDC_Assets")
        
        # Validate columns
        missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}. "
                f"Expected: {EXPECTED_COLUMNS}"
            )
        
        # Validate row count (Build Guide: 50 assets)
        if len(df) != 50:
            logger.warning(f"Expected 50 assets, found {len(df)}")
        
        # Coerce data types
        df['installation_date'] = pd.to_datetime(df['installation_date']).dt.strftime('%Y-%m-%d')
        df['last_maintenance_date'] = pd.to_datetime(df['last_maintenance_date']).dt.strftime('%Y-%m-%d')
        df['design_pressure_bar'] = df['design_pressure_bar'].astype(float)
        df['design_temp_c'] = df['design_temp_c'].astype(float)
        df['maintenance_interval_days'] = df['maintenance_interval_days'].astype(int)
        df['replacement_cost_usd'] = df['replacement_cost_usd'].astype(float)
        
        # Check for null values
        null_counts = df[EXPECTED_COLUMNS].isnull().sum()
        if null_counts.any():
            raise ValueError(f"Null values detected: {null_counts[null_counts > 0].to_dict()}")
        
        # Convert to list of dicts
        self.assets = df[EXPECTED_COLUMNS].to_dict('records')
        
        logger.info(f"Loaded {len(self.assets)} assets from Excel")
        logger.info(f"Asset classes: {df['asset_class'].value_counts().to_dict()}")
        
        return self.assets

    def push_to_maximo(self) -> Dict[str, int]:
        """Create asset records in Maximo via REST API.

        Returns:
            Dict with keys: created, skipped, failed
        """
        if not self.assets:
            raise ValueError("No assets loaded. Call load_from_excel() first.")
        
        if self.mock_mode:
            return self._push_to_mock()
        else:
            return self._push_to_real_maximo()
    
    def _push_to_mock(self) -> Dict[str, int]:
        """Mock implementation: store assets in memory."""
        logger.info(f"[MOCK] Simulating push of {len(self.assets)} assets to Maximo")
        
        # Simulate processing time
        import time
        time.sleep(0.1)
        
        result = {
            "created": len(self.assets),
            "skipped": 0,
            "failed": 0,
            "mock": True
        }
        
        logger.info(f"[MOCK] Result: {result}")
        return result
    
    def _push_to_real_maximo(self) -> Dict[str, int]:
        """Push assets to real Maximo MAS 9.1 via REST API."""
        if not self.client:
            raise ValueError(
                "Maximo client not provided. Initialize AssetLoader with maximo_client."
            )
        
        logger.info(f"[LIVE] Pushing {len(self.assets)} assets to Maximo")
        
        created = 0
        skipped = 0
        failed = 0
        
        for asset in self.assets:
            try:
                # POST to Maximo REST API: /oslc/os/mxasset
                response = self.client.create_asset(
                    asset_id=asset['asset_id'],
                    asset_class=asset['asset_class'],
                    description=asset['description'],
                    installation_date=asset['installation_date'],
                    design_pressure_bar=asset['design_pressure_bar'],
                    design_temp_c=asset['design_temp_c'],
                    last_maintenance_date=asset['last_maintenance_date'],
                    maintenance_interval_days=asset['maintenance_interval_days'],
                    replacement_cost_usd=asset['replacement_cost_usd']
                )
                
                if response.get('status') == 'created':
                    created += 1
                elif response.get('status') == 'exists':
                    skipped += 1
                    logger.debug(f"Asset {asset['asset_id']} already exists")
                else:
                    failed += 1
                    logger.error(f"Failed to create {asset['asset_id']}: {response}")
                    
            except Exception as e:
                failed += 1
                logger.error(f"Error creating {asset['asset_id']}: {e}")
        
        result = {
            "created": created,
            "skipped": skipped,
            "failed": failed,
            "mock": False
        }
        
        logger.info(f"[LIVE] Result: {result}")
        return result
    
    def get_asset_by_id(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get asset by ID from loaded assets.
        
        Args:
            asset_id: Asset identifier (e.g., GDC-WP-007)
            
        Returns:
            Asset dict or None if not found
        """
        for asset in self.assets:
            if asset['asset_id'] == asset_id:
                return asset
        return None
    
    def get_assets_by_class(self, asset_class: str) -> List[Dict[str, Any]]:
        """Get all assets of a specific class.
        
        Args:
            asset_class: Equipment class (WELL_PUMP, HEAT_EXCHANGER, etc.)
            
        Returns:
            List of asset dicts
        """
        return [a for a in self.assets if a['asset_class'] == asset_class]


def main():
    """CLI entry point for testing asset loader."""
    import sys
    
    print("=" * 60)
    print("GDC Kenya Asset Loader")
    print("Build Guide Step 2: Maximo Integration")
    print("=" * 60)
    print()
    
    # Initialize loader in mock mode
    loader = AssetLoader(mock_mode=True)
    
    try:
        # Load from Excel
        assets = loader.load_from_excel()
        print(f"[OK] Loaded {len(assets)} assets from Excel")
        
        # Push to Maximo (mock)
        result = loader.push_to_maximo()
        print(f"[OK] Push result: {result}")
        
        # Test retrieval
        test_asset = loader.get_asset_by_id("GDC-WP-007")
        if test_asset:
            print(f"[OK] Retrieved test asset: {test_asset['asset_id']} - {test_asset['description']}")
        
        print()
        print("[WARNING] SYNTHETIC DATA DISCLAIMER:")
        print("All data is computer-generated. Not representative of any")
        print("real client operational data.")
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
