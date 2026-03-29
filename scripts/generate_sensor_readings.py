#!/usr/bin/env python3
"""
Generate synthetic sensor readings dataset for OT Digital Twin.

Build Guide Dataset 2 (Lines 647-719): 43,800 rows of sensor data
- 10 assets × 4,380 hours each = 43,800 total rows
- 5-year hourly time series (2020-01-01 to 2024-12-31)
- Realistic degradation trends and pre-failure signatures
- NumPy seed 42 for reproducibility

Output: datasets/Sensor_Readings.xlsx
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Build Guide Lines 669-670: 10 representative assets
ASSETS = [
    "GDC-WP-001", "GDC-WP-002", "GDC-WP-003", "GDC-WP-004", "GDC-WP-005",
    "GDC-HX-001", "GDC-HX-002", "GDC-HX-003",
    "GDC-TU-001", "GDC-TU-002"
]

# Build Guide Lines 672-700: Sensor baselines per asset class
BASELINES = {
    "WP": {  # Well Pumps
        "temperature_c": 285.0,
        "pressure_bar": 45.0,
        "vibration_mm_s": 2.0,
        "flow_rate_kg_s": 120.0,
        "rotation_rpm": 3600,
        "health_score": 100.0
    },
    "HX": {  # Heat Exchangers
        "temperature_c": 240.0,
        "pressure_bar": 30.0,
        "vibration_mm_s": 1.5,
        "flow_rate_kg_s": 0.0,  # N/A
        "rotation_rpm": 0,  # N/A
        "health_score": 100.0
    },
    "TU": {  # Turbines
        "temperature_c": 215.0,
        "pressure_bar": 22.5,
        "vibration_mm_s": 1.8,
        "flow_rate_kg_s": 0.0,  # N/A
        "rotation_rpm": 3000,
        "health_score": 100.0
    }
}


def get_asset_baseline(asset_id: str) -> dict:
    """Get baseline values for an asset based on its class."""
    prefix = asset_id.split('-')[1][:2]
    return BASELINES.get(prefix, BASELINES["WP"])


def generate_sensor_timeseries(asset_id: str, hours: int = 4380) -> pd.DataFrame:
    """Generate realistic sensor time series with degradation trends.
    
    Build Guide Lines 674-677: Degradation pattern
    - Temperature drifts upward over time
    - Health score decreases
    - Vibration increases
    - Pre-failure signatures in final 720 hours (30 days)
    """
    baseline = get_asset_baseline(asset_id)
    
    # Start date: 2020-01-01 00:00
    start_date = datetime(2020, 1, 1, 0, 0, 0)
    timestamps = [start_date + timedelta(hours=i) for i in range(hours)]
    
    # Initialize arrays
    data = {
        'timestamp': timestamps,
        'asset_id': [asset_id] * hours
    }
    
    # Generate degradation trend (linear + noise)
    degradation_factor = np.linspace(0, 0.15, hours)  # 0% to 15% degradation over 5 years
    noise = np.random.normal(0, 0.02, hours)  # ±2% random noise
    
    # Temperature: increases with degradation
    temp_base = baseline['temperature_c']
    data['temperature_c'] = temp_base * (1 + degradation_factor + noise)
    
    # Pressure: slight seasonal variation
    pressure_base = baseline['pressure_bar']
    seasonal = 0.05 * np.sin(2 * np.pi * np.arange(hours) / (24 * 365))  # Annual cycle
    data['pressure_bar'] = pressure_base * (1 + seasonal + noise * 0.5)
    
    # Vibration: increases with degradation
    vib_base = baseline['vibration_mm_s']
    data['vibration_mm_s'] = vib_base * (1 + degradation_factor * 1.5 + np.abs(noise))
    
    # Flow rate: decreases with degradation (if applicable)
    flow_base = baseline['flow_rate_kg_s']
    if flow_base > 0:
        data['flow_rate_kg_s'] = flow_base * (1 - degradation_factor * 0.5 + noise * 0.3)
    else:
        data['flow_rate_kg_s'] = [0.0] * hours
    
    # Rotation RPM: slight increase with degradation (if applicable)
    rpm_base = baseline['rotation_rpm']
    if rpm_base > 0:
        data['rotation_rpm'] = (rpm_base * (1 + degradation_factor * 0.1 + noise * 0.02)).astype(int)
    else:
        data['rotation_rpm'] = [0] * hours
    
    # Health score: decreases linearly from 100 to ~40
    data['health_score'] = 100.0 - (degradation_factor * 60) + (noise * 5)
    data['health_score'] = np.clip(data['health_score'], 0, 100)
    
    # Failure labels: 1 in the 720 hours (30 days) before end, 0 otherwise
    # Build Guide Line 711: failure_label for LSTM training
    failure_window = 720  # 30 days
    data['failure_label'] = [1 if i >= (hours - failure_window) else 0 for i in range(hours)]
    
    # Failure event: 1 at the exact failure hour (last hour), 0 otherwise
    # Build Guide Line 716: failure_event for event analysis
    data['failure_event'] = [1 if i == (hours - 1) else 0 for i in range(hours)]
    
    df = pd.DataFrame(data)
    
    # Round to appropriate precision
    df['temperature_c'] = df['temperature_c'].round(2)
    df['pressure_bar'] = df['pressure_bar'].round(2)
    df['vibration_mm_s'] = df['vibration_mm_s'].round(2)
    df['flow_rate_kg_s'] = df['flow_rate_kg_s'].round(2)
    df['health_score'] = df['health_score'].round(1)
    
    return df


def main():
    """Generate complete sensor readings dataset."""
    print("=" * 70)
    print("OT Digital Twin - Sensor Readings Generator")
    print("=" * 70)
    print(f"Generating synthetic sensor data for {len(ASSETS)} assets...")
    print(f"Time range: 2020-01-01 to 2024-12-31 (4,380 hours per asset)")
    print(f"Total rows: {len(ASSETS)} × 4,380 = {len(ASSETS) * 4380:,}")
    print()
    
    # Generate data for all assets
    all_data = []
    for i, asset_id in enumerate(ASSETS, 1):
        print(f"[{i}/{len(ASSETS)}] Generating {asset_id}...", end=" ")
        df = generate_sensor_timeseries(asset_id, hours=4380)
        all_data.append(df)
        print(f"OK {len(df):,} rows")
    
    # Combine all assets
    print()
    print("Combining datasets...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Sort by timestamp, then asset_id
    combined_df = combined_df.sort_values(['timestamp', 'asset_id']).reset_index(drop=True)
    
    # Save to Excel
    output_path = Path(__file__).parent.parent / "datasets" / "Sensor_Readings.xlsx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving to {output_path}...")
    combined_df.to_excel(output_path, index=False, engine='openpyxl')
    
    print()
    print("=" * 70)
    print("SUCCESS: Dataset generation complete!")
    print("=" * 70)
    print(f"Output file: {output_path}")
    print(f"Total rows: {len(combined_df):,}")
    print(f"Date range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
    print(f"Assets: {combined_df['asset_id'].nunique()}")
    print(f"Failure events: {combined_df['failure_event'].sum()}")
    print()
    print("Column summary:")
    print(combined_df.dtypes)
    print()
    print("Sample data (first 5 rows):")
    print(combined_df.head())
    print()
    print("WARNING: SYNTHETIC DATA - All readings are computer-generated.")
    print("         Not representative of any real client operational data.")


if __name__ == "__main__":
    main()

# Made with Bob
