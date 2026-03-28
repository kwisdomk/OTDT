"""Generate GDC_Assets.xlsx with 50 geothermal equipment records.

Build Guide Step 2: Dataset 1 (Lines 573-644)
Creates synthetic GDC Kenya asset inventory matching Maximo APM hierarchy.

⚠️ SYNTHETIC DATA: All data is computer-generated. Not representative
of any real client operational data.
"""
import pandas as pd
from datetime import datetime, timedelta
import random
from pathlib import Path

# Set random seed for reproducibility
random.seed(42)

# Build Guide Lines 579-644: Column specifications
COLUMNS = [
    "asset_id",
    "asset_class", 
    "description",
    "installation_date",
    "design_pressure_bar",
    "design_temp_c",
    "last_maintenance_date",
    "maintenance_interval_days",
    "replacement_cost_usd",
    "unity_object_name"
]

# Build Guide Lines 589-595: Asset class distribution
ASSET_CLASSES = {
    "WELL_PUMP": {
        "count": 20,
        "prefix": "WP",
        "description_template": "Geothermal Well Pump {} - Olkaria {}",
        "design_pressure_range": (35.0, 55.0),
        "design_temp_range": (250.0, 300.0),
        "replacement_cost_range": (150000.0, 200000.0),
        "maintenance_interval_range": (60, 90),
        "unity_prefix": "WellPump_"
    },
    "HEAT_EXCHANGER": {
        "count": 10,
        "prefix": "HX",
        "description_template": "Heat Exchanger {} - Olkaria Geothermal Plant",
        "design_pressure_range": (20.0, 40.0),
        "design_temp_range": (200.0, 280.0),
        "replacement_cost_range": (100000.0, 150000.0),
        "maintenance_interval_range": (90, 120),
        "unity_prefix": "HeatExchanger_"
    },
    "TURBINE": {
        "count": 10,
        "prefix": "TU",
        "description_template": "Steam Turbine {} - Power Generation Unit",
        "design_pressure_range": (15.0, 30.0),
        "design_temp_range": (180.0, 250.0),
        "replacement_cost_range": (300000.0, 500000.0),
        "maintenance_interval_range": (120, 180),
        "unity_prefix": "Turbine_"
    },
    "PRODUCTION_PIPE": {
        "count": 10,
        "prefix": "PP",
        "description_template": "Production Pipeline {} - Steam Transport",
        "design_pressure_range": (40.0, 70.0),
        "design_temp_range": (280.0, 350.0),
        "replacement_cost_range": (50000.0, 100000.0),
        "maintenance_interval_range": (30, 60),
        "unity_prefix": "ProductionPipe_"
    }
}

# Build Guide Line 607: Installation date range 2014-2022
INSTALLATION_START = datetime(2014, 1, 1)
INSTALLATION_END = datetime(2022, 12, 31)

# Olkaria geothermal fields for realistic descriptions
OLKARIA_FIELDS = ["I", "II", "III", "IV", "V"]


def generate_asset_record(asset_class: str, asset_number: int, config: dict) -> dict:
    """Generate a single asset record with realistic geothermal parameters.
    
    Args:
        asset_class: Equipment class (WELL_PUMP, HEAT_EXCHANGER, etc.)
        asset_number: Sequential number for this asset class
        config: Configuration dict from ASSET_CLASSES
        
    Returns:
        Dict with all 10 required columns
    """
    # Asset ID: GDC-{PREFIX}-{NNN} (Build Guide Line 589)
    asset_id = f"GDC-{config['prefix']}-{asset_number:03d}"
    
    # Description with Olkaria field reference
    if asset_class == "WELL_PUMP":
        field = random.choice(OLKARIA_FIELDS)
        description = config['description_template'].format(asset_number, field)
    else:
        description = config['description_template'].format(asset_number)
    
    # Installation date: random date between 2014-2022 (Build Guide Line 607)
    days_range = (INSTALLATION_END - INSTALLATION_START).days
    random_days = random.randint(0, days_range)
    installation_date = INSTALLATION_START + timedelta(days=random_days)
    
    # Design parameters: random within realistic ranges
    design_pressure_bar = round(random.uniform(*config['design_pressure_range']), 1)
    design_temp_c = round(random.uniform(*config['design_temp_range']), 1)
    
    # Last maintenance: random date in last 6 months (Build Guide Line 625)
    days_ago = random.randint(30, 180)
    last_maintenance_date = datetime.now() - timedelta(days=days_ago)
    
    # Maintenance interval: random within class range (Build Guide Line 631)
    maintenance_interval_days = random.randint(*config['maintenance_interval_range'])
    
    # Replacement cost: random within class range (Build Guide Line 637)
    replacement_cost_usd = round(random.uniform(*config['replacement_cost_range']), 2)
    
    # Unity object name: matches GameObject in Unity scene (Build Guide Line 643)
    unity_object_name = f"{config['unity_prefix']}{asset_number:02d}"
    
    return {
        "asset_id": asset_id,
        "asset_class": asset_class,
        "description": description,
        "installation_date": installation_date.strftime("%Y-%m-%d"),
        "design_pressure_bar": design_pressure_bar,
        "design_temp_c": design_temp_c,
        "last_maintenance_date": last_maintenance_date.strftime("%Y-%m-%d"),
        "maintenance_interval_days": maintenance_interval_days,
        "replacement_cost_usd": replacement_cost_usd,
        "unity_object_name": unity_object_name
    }


def generate_gdc_assets() -> pd.DataFrame:
    """Generate all 50 GDC Kenya asset records.
    
    Returns:
        DataFrame with 50 rows, 10 columns per Build Guide specification
    """
    assets = []
    
    for asset_class, config in ASSET_CLASSES.items():
        for i in range(1, config['count'] + 1):
            asset = generate_asset_record(asset_class, i, config)
            assets.append(asset)
    
    df = pd.DataFrame(assets, columns=COLUMNS)
    
    # Validate: exactly 50 assets (Build Guide requirement)
    assert len(df) == 50, f"Expected 50 assets, got {len(df)}"
    
    # Validate: all columns present
    assert list(df.columns) == COLUMNS, "Column mismatch"
    
    # Validate: no null values
    assert df.isnull().sum().sum() == 0, "Null values detected"
    
    # Validate: unique asset IDs
    assert df['asset_id'].nunique() == 50, "Duplicate asset IDs detected"
    
    return df


def main():
    """Generate GDC_Assets.xlsx and save to datasets/ directory."""
    print("=" * 60)
    print("GDC Kenya Asset Inventory Generator")
    print("Build Guide Step 2: Dataset 1 (Lines 573-644)")
    print("=" * 60)
    print()
    
    # Generate assets
    print("Generating 50 GDC Kenya geothermal equipment records...")
    df = generate_gdc_assets()
    
    # Summary statistics
    print(f"[OK] Generated {len(df)} assets")
    print(f"[OK] Asset classes: {df['asset_class'].value_counts().to_dict()}")
    print(f"[OK] Installation date range: {df['installation_date'].min()} to {df['installation_date'].max()}")
    print(f"[OK] Total replacement value: ${df['replacement_cost_usd'].sum():,.2f}")
    print()
    
    # Save to Excel
    output_path = Path(__file__).parent.parent / "datasets" / "GDC_Assets.xlsx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving to: {output_path}")
    df.to_excel(output_path, index=False, sheet_name="GDC_Assets")
    
    print("[OK] GDC_Assets.xlsx created successfully")
    print()
    print("[WARNING] SYNTHETIC DATA DISCLAIMER:")
    print("All data is computer-generated. Not representative of any")
    print("real client operational data.")
    print()
    print("=" * 60)
    print("Next step: Run validation script")
    print("  PowerShell: .\\scripts\\validate_gdc_assets.ps1")
    print("=" * 60)


if __name__ == "__main__":
    main()

# Made with Bob
