# GDC KENYA ASSET REFERENCE

**50 Geothermal Assets - Complete Specification**  
**Location**: GDC Kenya Olkaria Geothermal Facility  
**Last Updated**: March 24, 2026

---

## 📊 ASSET OVERVIEW

| Asset Type | Count | ID Range | Primary Function |
|------------|-------|----------|------------------|
| Well Pumps | 20 | GDC-WP-001 to GDC-WP-020 | Extract geothermal fluid from wells |
| Heat Exchangers | 10 | GDC-HX-001 to GDC-HX-010 | Transfer heat from geothermal fluid |
| Turbines | 10 | GDC-TU-001 to GDC-TU-010 | Generate electricity from steam |
| Production Pipes | 10 | GDC-PP-001 to GDC-PP-010 | Transport geothermal fluid |

**Total Assets**: 50  
**Demo Asset**: Well Pump WP-07 (`GDC-WP-007`)

---

## 🔧 WELL PUMPS (20 Assets)

### Asset IDs: GDC-WP-001 through GDC-WP-020

#### Function:
Extract geothermal fluid from production wells at depths of 1,500-3,000 meters.

#### Standard Sensor Configuration:
```json
{
  "temperature_c": 85.0,      // Fluid temperature (normal: 80-95°C)
  "pressure_bar": 72.0,       // Pump discharge pressure (normal: 65-80 bar)
  "vibration_mm_s": 3.8,      // Pump vibration (normal: 2.0-5.0 mm/s)
  "flow_rate_kg_s": 45.0,     // Fluid flow rate (normal: 40-50 kg/s)
  "rotation_rpm": 1800,       // Pump speed (normal: 1750-1850 RPM)
  "health_score": 0.92,       // Overall health (0.0-1.0)
  "failure_label": 0,         // Binary failure indicator
  "failure_event": false      // Event flag
}
```

#### Critical Thresholds:
- Temperature: > 105°C (CRITICAL)
- Pressure: > 85 bar (CRITICAL)
- Vibration: > 7.5 mm/s (CRITICAL)
- Flow rate: < 35 kg/s (WARNING)
- Rotation: < 1700 or > 1900 RPM (WARNING)

#### Common Failure Modes:
1. Bearing wear (vibration increase)
2. Seal degradation (pressure drop)
3. Impeller damage (flow rate decrease)
4. Motor overheating (temperature spike)

#### Maintenance Schedule:
- Routine inspection: Every 30 days
- Bearing replacement: Every 180 days
- Complete overhaul: Every 365 days

---

## 🔥 HEAT EXCHANGERS (10 Assets)

### Asset IDs: GDC-HX-001 through GDC-HX-010

#### Function:
Transfer thermal energy from geothermal fluid to secondary working fluid (typically isobutane or pentane).

#### Standard Sensor Configuration:
```json
{
  "temperature_c": 165.0,     // Primary fluid temp (normal: 155-175°C)
  "pressure_bar": 18.0,       // Shell side pressure (normal: 15-22 bar)
  "vibration_mm_s": 2.1,      // Structural vibration (normal: 1.0-3.0 mm/s)
  "flow_rate_kg_s": 120.0,    // Primary fluid flow (normal: 110-130 kg/s)
  "rotation_rpm": 0,          // N/A for heat exchangers
  "health_score": 0.88,       // Overall health
  "failure_label": 0,
  "failure_event": false
}
```

#### Critical Thresholds:
- Temperature: > 190°C (CRITICAL)
- Pressure: > 25 bar (CRITICAL)
- Vibration: > 5.0 mm/s (WARNING)
- Flow rate: < 100 kg/s (WARNING)

#### Common Failure Modes:
1. Tube fouling (heat transfer efficiency drop)
2. Tube leakage (pressure loss)
3. Corrosion (structural integrity)
4. Scaling (flow restriction)

#### Maintenance Schedule:
- Chemical cleaning: Every 90 days
- Tube inspection: Every 180 days
- Complete retubing: Every 730 days

---

## ⚡ TURBINES (10 Assets)

### Asset IDs: GDC-TU-001 through GDC-TU-010

#### Function:
Convert thermal energy from steam into mechanical rotation, driving electrical generators.

#### Standard Sensor Configuration:
```json
{
  "temperature_c": 245.0,     // Steam inlet temp (normal: 235-255°C)
  "pressure_bar": 68.0,       // Steam inlet pressure (normal: 60-75 bar)
  "vibration_mm_s": 4.2,      // Bearing vibration (normal: 3.0-5.5 mm/s)
  "flow_rate_kg_s": 42.0,     // Steam flow rate (normal: 38-48 kg/s)
  "rotation_rpm": 3000,       // Turbine speed (normal: 2950-3050 RPM)
  "health_score": 0.90,       // Overall health
  "failure_label": 0,
  "failure_event": false
}
```

#### Critical Thresholds:
- Temperature: > 280°C (CRITICAL)
- Pressure: > 85 bar (CRITICAL)
- Vibration: > 7.1 mm/s (CRITICAL)
- Flow rate: < 35 kg/s (WARNING)
- Rotation: < 2900 or > 3100 RPM (CRITICAL)

#### Common Failure Modes:
1. Blade erosion (efficiency loss)
2. Bearing failure (vibration spike)
3. Seal degradation (steam leakage)
4. Rotor imbalance (vibration increase)

#### Maintenance Schedule:
- Vibration monitoring: Continuous
- Bearing inspection: Every 60 days
- Blade inspection: Every 180 days
- Major overhaul: Every 365 days

---

## 🚰 PRODUCTION PIPES (10 Assets)

### Asset IDs: GDC-PP-001 through GDC-PP-010

#### Function:
Transport geothermal fluid from wellheads to processing facilities and between plant components.

#### Standard Sensor Configuration:
```json
{
  "temperature_c": 195.0,     // Fluid temperature (normal: 180-210°C)
  "pressure_bar": 55.0,       // Internal pressure (normal: 48-62 bar)
  "vibration_mm_s": 1.5,      // Pipe vibration (normal: 0.5-2.5 mm/s)
  "flow_rate_kg_s": 85.0,     // Fluid flow rate (normal: 75-95 kg/s)
  "rotation_rpm": 0,          // N/A for pipes
  "health_score": 0.94,       // Overall health
  "failure_label": 0,
  "failure_event": false
}
```

#### Critical Thresholds:
- Temperature: > 230°C (CRITICAL)
- Pressure: > 70 bar (CRITICAL)
- Vibration: > 4.0 mm/s (WARNING)
- Flow rate: < 65 kg/s (WARNING)

#### Common Failure Modes:
1. Corrosion (wall thinning)
2. Thermal expansion cracks
3. Joint leakage
4. Scaling (flow restriction)

#### Maintenance Schedule:
- Ultrasonic thickness testing: Every 90 days
- Joint inspection: Every 180 days
- Internal cleaning: Every 365 days

---

## 🎯 DEMO ASSET: WELL PUMP WP-07

### Asset ID: GDC-WP-007

#### Location:
Production Well 7, GDC Kenya Olkaria Facility, Sector B

#### Installation Date:
January 15, 2024

#### Current Status:
Operational - 450 days since last major maintenance

#### Normal Operating Parameters:
```json
{
  "asset_id": "GDC-WP-007",
  "asset_type": "well_pump",
  "asset_label": "Well Pump 7 - Production Well B",
  "location": "Olkaria Sector B",
  "sensors": {
    "temperature_c": 85.0,
    "pressure_bar": 72.0,
    "vibration_mm_s": 3.8,
    "flow_rate_kg_s": 45.0,
    "rotation_rpm": 1800,
    "health_score": 0.92,
    "failure_label": 0,
    "failure_event": false
  }
}
```

#### Demo Anomaly Scenario:
**Bearing Degradation Event**

**Timeline**:
- T+0s: Normal operation (all sensors green)
- T+60s: Anomaly injection begins
- T+61s: Anomaly AI detects critical condition
- T+62s: Monte Carlo simulation runs (10,000 iterations)
- T+63s: Failure probability calculated: 34%
- T+64s: Maximo work order auto-created
- T+120s: Anomaly cleared (demo reset)

**Anomaly Parameters**:
```json
{
  "temperature_c": 108.0,     // +23°C spike (bearing friction)
  "pressure_bar": 78.0,       // +6 bar increase (flow restriction)
  "vibration_mm_s": 9.5,      // +5.7 mm/s spike (bearing wear)
  "flow_rate_kg_s": 38.0,     // -7 kg/s drop (efficiency loss)
  "rotation_rpm": 1650,       // -150 RPM decrease (load increase)
  "health_score": 0.34,       // Degraded to critical
  "failure_label": 1,         // Failure imminent
  "failure_event": true       // Event triggered
}
```

**Expected Demo Results**:
- Anomaly detection latency: < 1 second
- Monte Carlo execution time: < 5 seconds
- Failure probability: 34% (immediate) → 67% (if delayed 7 days)
- Recommended action: SCHEDULE_MAINTENANCE
- Optimal maintenance date: 7 days from detection
- Work order ID: Auto-generated in Maximo
- Estimated maintenance cost: USD 12,000
- Prevented failure cost: USD 180,000
- ROI: 1,400% for this single intervention

---

## 📊 ASSET HEALTH SCORING

### Health Score Calculation:
```python
health_score = weighted_average([
    sensor_deviation_score * 0.40,    # How far from normal
    trend_analysis_score * 0.30,      # Rate of change
    maintenance_history_score * 0.20, # Past reliability
    operating_hours_score * 0.10      # Age factor
])
```

### Health Score Ranges:
- **0.90 - 1.00**: Excellent (GREEN)
- **0.75 - 0.89**: Good (GREEN)
- **0.60 - 0.74**: Fair (YELLOW)
- **0.40 - 0.59**: Poor (ORANGE)
- **0.00 - 0.39**: Critical (RED)

---

## 🔄 ASSET STATE MESSAGE FORMAT

### WebSocket Broadcast Format:
```json
{
  "timestamp": "2026-03-24T11:00:00.000Z",
  "assets": [
    {
      "asset_id": "GDC-WP-007",
      "asset_type": "well_pump",
      "asset_label": "Well Pump 7 - Production Well B",
      "status": "CRITICAL",
      "colour_hex": "#C00000",
      "sensors": {
        "temperature_c": 108.0,
        "pressure_bar": 78.0,
        "vibration_mm_s": 9.5,
        "flow_rate_kg_s": 38.0,
        "rotation_rpm": 1650,
        "health_score": 0.34,
        "failure_label": 1,
        "failure_event": true
      },
      "anomaly_score": 0.98,
      "failure_probability": 0.34,
      "days_to_failure_p50": 7,
      "days_to_failure_p95": 4,
      "recommended_action": "SCHEDULE_MAINTENANCE",
      "optimal_maintenance_day": "2026-03-31",
      "active_work_order_id": "WO-2026-00142"
    }
    // ... 49 more assets
  ]
}
```

---

## 🎨 ASSET VISUALIZATION

### Color Coding:
- **GREEN (#1E6B3C)**: Normal operation (health_score > 0.75)
- **YELLOW (#FF9900)**: Warning (health_score 0.60-0.75)
- **RED (#C00000)**: Critical (health_score < 0.60)

### Unity 3D Scene Layout:
```
GDC_Plant_Scene
├── WellPumps/
│   ├── GDC-WP-001 (GameObject)
│   ├── GDC-WP-002 (GameObject)
│   └── ... (18 more)
├── HeatExchangers/
│   ├── GDC-HX-001 (GameObject)
│   └── ... (9 more)
├── Turbines/
│   ├── GDC-TU-001 (GameObject)
│   └── ... (9 more)
└── ProductionPipes/
    ├── GDC-PP-001 (GameObject)
    └── ... (9 more)
```

### Three.js Web Viewer:
- Grid layout: 10 columns × 5 rows
- Asset cards with real-time color updates
- Click to expand sensor details
- Hover to show health score tooltip

---

## 📝 IMPLEMENTATION NOTES

### Simulator Configuration:
Each asset type requires specific sensor ranges and failure patterns. See `sensor_simulator/assets/` directory for JSON configuration files.

### Database Schema:
```sql
CREATE TABLE assets (
    asset_id TEXT PRIMARY KEY,
    asset_type TEXT NOT NULL,
    asset_label TEXT,
    location TEXT,
    installation_date DATE,
    last_maintenance_date DATE
);

CREATE TABLE sensor_readings (
    time TIMESTAMPTZ NOT NULL,
    asset_id TEXT NOT NULL,
    sensor_name TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

SELECT create_hypertable('sensor_readings', 'time');
```

### Redis Cache Structure:
```
Key: asset:GDC-WP-007
Value: {JSON asset state}
TTL: 60 seconds
```

---

**Last Updated**: March 24, 2026  
**Authority**: Philip Mukiti, CEO i3 Technologies  
**Source**: GDC Kenya Technical Specifications