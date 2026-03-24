# OT DIGITAL TWIN - CORRECTED SPECIFICATIONS

**CRITICAL UPDATE**: March 24, 2026  
**Source**: Philip's Official Build Documentation  
**Status**: These are the OFFICIAL specifications - all previous docs must align with this

---

## 🚨 CRITICAL CORRECTIONS FROM PHILIP'S OFFICIAL SPEC

### 1. ASSET STRUCTURE (CORRECTED)

**❌ WRONG (Previous)**: Single turbine `GDC-TURBINE-01`

**✅ CORRECT (Official)**: **50 GDC Kenya Geothermal Assets**

#### Asset Breakdown:
- **20 Well Pumps**: `GDC-WP-001` through `GDC-WP-020`
- **10 Heat Exchangers**: `GDC-HX-001` through `GDC-HX-010`
- **10 Turbines**: `GDC-TU-001` through `GDC-TU-010`
- **10 Production Pipes**: `GDC-PP-001` through `GDC-PP-010`

#### Demo Asset:
**Well Pump WP-07** (`GDC-WP-007`)  
NOT turbine bearing as previously documented

---

### 2. SENSOR FIELD NAMES (CORRECTED)

**❌ WRONG (Previous)**:
```json
{
  "bearing_vibration_mms": 4.2,
  "bearing_temp_c": 83,
  "temperature_turbine_inlet": 245,
  "steam_inlet_pressure_bar": 68,
  "turbine_rpm": 3000,
  "steam_flow_kgs": 42
}
```

**✅ CORRECT (Official)**:
```json
{
  "temperature_c": 83.5,
  "pressure_bar": 68.2,
  "vibration_mm_s": 4.2,
  "flow_rate_kg_s": 42.0,
  "rotation_rpm": 3000,
  "health_score": 0.85,
  "failure_label": 0,
  "failure_event": false
}
```

#### Field Definitions:
- `temperature_c` - Temperature in Celsius
- `pressure_bar` - Pressure in bar
- `vibration_mm_s` - Vibration in millimeters per second
- `flow_rate_kg_s` - Flow rate in kilograms per second
- `rotation_rpm` - Rotation speed in RPM
- `health_score` - Overall health score (0.0 to 1.0)
- `failure_label` - Binary failure indicator (0 or 1)
- `failure_event` - Boolean failure event flag

---

### 3. TRAINING DATA (CORRECTED)

**❌ WRONG (Previous)**: Generate synthetic data from scratch using data_generator.py

**✅ CORRECT (Official)**: **43,800 rows of real synthetic sensor data already exists**

#### Location:
The MVP Tracker Excel file (`06_Sprint_Tracker.xlsx`) contains the complete training dataset.

#### Dataset Specifications:
- **Total Rows**: 43,800
- **Format**: Ready for direct import into Watson Studio
- **Coverage**: Multiple failure scenarios across all asset types
- **Time Period**: Sufficient historical data for LSTM training

#### Action Required:
1. Extract data from Excel file
2. Convert to CSV format
3. Load directly into Watson Studio
4. NO need to generate new synthetic data

---

### 4. SUCCESS METRICS (CORRECTED)

**❌ WRONG (Previous)**: Generic targets without specific numbers

**✅ CORRECT (Official)**: Specific, measurable targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| LSTM AUC-ROC | > 0.82 | Model validation accuracy |
| Monte Carlo Speed | 10,000 runs in < 5s | Execution time |
| What-If Response | < 2 seconds | API response latency |
| Sensor Update Latency | < 1 second | End-to-end pipeline |
| Anomaly Detection | > 80% | Detection accuracy |
| Demo ROI Figure | 650% | Business case metric |

---

### 5. ROI NUMBERS (CORRECTED)

**❌ WRONG (Previous)**:
- Generic $8.2M downtime
- Generic $150K maintenance
- No specific ROI calculation

**✅ CORRECT (Official)**:

#### Cost Structure:
- **Unplanned Failure Cost**: USD 180,000 per event
- **Platform Annual Cost**: USD 48,000/year
- **Prevented Failures**: 2 per year (conservative estimate)

#### ROI Calculation:
```
Annual Savings = 2 failures × USD 180,000 = USD 360,000
Platform Cost = USD 48,000/year
Net Benefit = USD 360,000 - USD 48,000 = USD 312,000
ROI = (USD 312,000 / USD 48,000) × 100 = 650%
```

**Official ROI: 650%**

These exact numbers MUST be used in:
- Demo script
- CEO brief
- Business case presentations
- Client proposals

---

### 6. BROWSER ACCESS (CORRECTED)

**❌ WRONG (Previous)**: Unity WebGL export question unanswered

**✅ CORRECT (Official)**: **Three.js web viewer is part of the MVP**

#### Architecture:
- **Primary**: Unity XR for immersive visualization
- **Secondary**: Three.js web viewer for browser access
- **Use Case**: Clients without Unity get browser URL via Three.js

#### Implementation Requirements:
```
frontend/
├── react-dashboard/     # Existing
├── unity-twin/          # Existing
└── threejs-viewer/      # NEW - Required for MVP
    ├── src/
    │   ├── scene.js
    │   ├── assets.js
    │   └── websocket.js
    └── package.json
```

#### Three.js Viewer Features:
- WebSocket connection to FastAPI
- 3D asset visualization
- Real-time color updates (green/yellow/red)
- Sensor data overlay
- Failure probability display

---

## 📋 UPDATED SYSTEM ARCHITECTURE

### Data Flow (Corrected):
```
50 GDC Assets (WP/HX/TU/PP) 
    ↓
OPC-UA Simulator (Multi-asset)
    ↓
Watson IoT Platform (MQTT)
    ↓
Kafka (ot-twin-sensors topic)
    ↓
FastAPI Backend
    ├→ Anomaly AI (8 sensor fields)
    ├→ Monte Carlo Engine (10k runs < 5s)
    └→ LSTM Predictor (AUC-ROC > 0.82)
    ↓
WebSocket /twin/stream
    ├→ React Dashboard
    ├→ Unity XR Twin
    └→ Three.js Web Viewer (NEW)
```

---

## 🎯 DEMO ASSET SPECIFICATION

### Well Pump WP-07 (`GDC-WP-007`)

#### Normal Operating Parameters:
```json
{
  "asset_id": "GDC-WP-007",
  "asset_type": "well_pump",
  "location": "GDC Kenya Olkaria Facility",
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

#### Anomaly Injection (Demo):
```json
{
  "temperature_c": 108.0,    // +23°C spike
  "pressure_bar": 78.0,      // +6 bar increase
  "vibration_mm_s": 9.5,     // Critical threshold breach
  "flow_rate_kg_s": 38.0,    // -7 kg/s drop
  "rotation_rpm": 1650,      // -150 RPM decrease
  "health_score": 0.34,      // Degraded
  "failure_label": 1,        // Failure imminent
  "failure_event": true      // Event triggered
}
```

#### Expected Demo Results:
- Anomaly detection: < 1 second
- Monte Carlo probability: 34% → 67% (if delayed)
- Recommended action: SCHEDULE_MAINTENANCE
- Optimal maintenance date: 7 days from detection
- Work order auto-created in Maximo

---

## 📊 UPDATED FILE STRUCTURE

### Sensor Simulator (Corrected):
```
sensor_simulator/
├── simulator.py              # Multi-asset simulator (50 assets)
├── watson_iot_publisher.py   # MQTT publisher
├── anomaly_injector.py       # Demo anomaly for WP-07
├── config.py                 # Asset definitions + sensor schema
└── assets/
    ├── well_pumps.json       # 20 well pump configs
    ├── heat_exchangers.json  # 10 heat exchanger configs
    ├── turbines.json         # 10 turbine configs
    └── production_pipes.json # 10 pipe configs
```

### Frontend (Corrected):
```
frontend/
├── react-dashboard/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AssetGrid.jsx        # 50-asset overview
│   │   │   ├── SensorGauges.jsx     # 8 sensor fields
│   │   │   ├── WhatIfSlider.jsx     # Existing
│   │   │   └── WorkOrderPanel.jsx   # Existing
│   │   └── hooks/
│   │       └── useWebSocket.js      # Existing
│   └── package.json
├── unity-twin/                       # Existing
└── threejs-viewer/                   # NEW - Required
    ├── src/
    │   ├── main.js
    │   ├── AssetRenderer.js
    │   ├── WebSocketClient.js
    │   └── SensorOverlay.js
    ├── public/
    │   └── models/                   # 3D asset models
    └── package.json
```

---

## 🔄 MIGRATION CHECKLIST

### Phase 1: Documentation Updates
- [x] Create CORRECTED_SPECIFICATIONS.md
- [ ] Update BUILD_PLAN.md
- [ ] Update PROJECT_SUMMARY.md
- [ ] Update PHASE_1_FOUNDATION.md
- [ ] Update demo script (05_Demo_Script.docx)

### Phase 2: Code Updates
- [ ] Update sensor_simulator/config.py (50 assets)
- [ ] Update sensor field names across all Python files
- [ ] Update FastAPI models (8 sensor fields)
- [ ] Update React components (8 sensor fields)
- [ ] Update Unity SensorBridge.cs (8 sensor fields)

### Phase 3: New Components
- [ ] Create Three.js web viewer
- [ ] Create asset configuration files (JSON)
- [ ] Update WebSocket message format (50 assets)

### Phase 4: Data Pipeline
- [ ] Extract 43,800-row dataset from Excel
- [ ] Convert to CSV format
- [ ] Upload to Watson Studio
- [ ] Update LSTM training notebook

---

## 📝 COMMIT MESSAGE TEMPLATE

When updating files, use this format:
```
fix(docs): align with Philip's official spec - [component]

BREAKING CHANGE: Asset structure changed from 1 turbine to 50 GDC assets
- Updated sensor field names to official convention
- Corrected ROI figures to 650% (USD 180k/360k/48k)
- Added Three.js web viewer requirement
- Updated success metrics with specific targets

Refs: Philip's Official Build Documentation
```

---

## ⚠️ CRITICAL NOTES

1. **DO NOT start coding** until all documentation is updated
2. **All team members** must review this corrected spec
3. **Demo script** must use exact ROI numbers (650%, USD 180k, USD 48k)
4. **Training data** is ready - do not regenerate
5. **Three.js viewer** is NOT optional - it's part of MVP
6. **Demo asset** is WP-07, not turbine bearing

---

## 📞 QUESTIONS?

If anything is unclear, refer to:
1. This document (CORRECTED_SPECIFICATIONS.md)
2. Philip's official build docs (1_phase/ folder)
3. MVP Tracker (build guides/06_Sprint_Tracker.xlsx)

**Last Updated**: March 24, 2026  
**Status**: OFFICIAL SPECIFICATION  
**Authority**: Philip Mukiti (CEO, i3 Technologies)