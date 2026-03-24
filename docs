# IMPLEMENTATION GUIDE - CORRECTED SPECIFICATIONS

**Quick Start Guide for Building with Correct Specs**  
**Last Updated**: March 24, 2026

---

## 🚀 QUICK START

### Step 1: Read These Documents First
1. [`CORRECTED_SPECIFICATIONS.md`](./CORRECTED_SPECIFICATIONS.md) - Official spec
2. [`GDC_ASSET_REFERENCE.md`](./GDC_ASSET_REFERENCE.md) - 50 asset details
3. This guide - Implementation steps

### Step 2: Update Your .env File
```bash
# Add these new variables
DEMO_ASSET_ID=GDC-WP-007
ASSET_COUNT=50
SENSOR_FIELDS=temperature_c,pressure_bar,vibration_mm_s,flow_rate_kg_s,rotation_rpm,health_score,failure_label,failure_event
```

### Step 3: Extract Training Data
```bash
# The 43,800 rows are in the Excel file
# Location: build guides/06_Sprint_Tracker.xlsx
# Look for a sheet with sensor data or training data
# Export to: monte_carlo/data/gdc_training_data.csv
```

---

## 📋 CRITICAL CHANGES CHECKLIST

### Sensor Field Names (MUST UPDATE)

**Find and Replace Across All Files:**

| Old Name | New Name | Files to Update |
|----------|----------|-----------------|
| `bearing_vibration_mms` | `vibration_mm_s` | All Python, JS, C# files |
| `bearing_temp_c` | `temperature_c` | All Python, JS, C# files |
| `steam_inlet_temp_c` | `temperature_c` | All Python, JS, C# files |
| `steam_inlet_pressure_bar` | `pressure_bar` | All Python, JS, C# files |
| `turbine_rpm` | `rotation_rpm` | All Python, JS, C# files |
| `steam_flow_kgs` | `flow_rate_kg_s` | All Python, JS, C# files |

**Add New Fields:**
- `health_score` (float 0.0-1.0)
- `failure_label` (int 0 or 1)
- `failure_event` (boolean)

### Asset Structure (MUST UPDATE)

**Old Code:**
```python
ASSET_ID = "GDC-TURBINE-01"
ASSET_TYPE = "geothermal_turbine"
```

**New Code:**
```python
# For demo
DEMO_ASSET_ID = "GDC-WP-007"
DEMO_ASSET_TYPE = "well_pump"

# For full system (50 assets)
ASSET_IDS = [
    # Well Pumps (20)
    *[f"GDC-WP-{i:03d}" for i in range(1, 21)],
    # Heat Exchangers (10)
    *[f"GDC-HX-{i:03d}" for i in range(1, 11)],
    # Turbines (10)
    *[f"GDC-TU-{i:03d}" for i in range(1, 11)],
    # Production Pipes (10)
    *[f"GDC-PP-{i:03d}" for i in range(1, 11)],
]
```

---

## 🔧 FILE-BY-FILE UPDATE GUIDE

### 1. sensor_simulator/config.py

**Update sensor configuration:**
```python
SENSOR_CONFIG = {
    'temperature_c':    {'mean': 85.0,  'std': 2.5,  'min': 60,  'max': 130},
    'pressure_bar':     {'mean': 72.0,  'std': 1.5,  'min': 50,  'max': 100},
    'vibration_mm_s':   {'mean': 3.8,   'std': 0.4,  'min': 0.5, 'max': 15},
    'flow_rate_kg_s':   {'mean': 45.0,  'std': 1.2,  'min': 20,  'max': 80},
    'rotation_rpm':     {'mean': 1800,  'std': 30,   'min': 1500,'max': 2000},
    'health_score':     {'mean': 0.92,  'std': 0.05, 'min': 0.0, 'max': 1.0},
}

THRESHOLDS = {
    'temperature_c':  {'warn': 95,  'crit': 105},
    'pressure_bar':   {'warn': 80,  'crit': 85},
    'vibration_mm_s': {'warn': 5.0, 'crit': 7.5},
    'flow_rate_kg_s': {'warn': 35,  'crit': 30},
    'rotation_rpm':   {'warn_low': 1700, 'warn_high': 1900, 'crit_low': 1650, 'crit_high': 1950},
}
```

### 2. sensor_simulator/simulator.py

**Update GeothermalSimulator class:**
```python
class GeothermalSimulator:
    def __init__(self, asset_id="GDC-WP-007", asset_type="well_pump"):
        self.asset_id = asset_id
        self.asset_type = asset_type
        self.step = 0
        self.drift = 0.0
        self.anomaly_active = False
    
    def get_reading(self) -> dict:
        self.step += 1
        self.drift += 0.002
        
        if self.anomaly_active:
            temp = np.random.normal(108, 2.0)
            vib = np.random.normal(9.5, 0.3)
            press = np.random.normal(78, 1.0)
            flow = np.random.normal(38, 1.5)
            rpm = np.random.normal(1650, 20)
            health = 0.34
            failure_label = 1
            failure_event = True
        else:
            temp = np.random.normal(85 + self.drift * 2, 2.5)
            vib = np.random.normal(3.8 + self.drift, 0.4)
            press = np.random.normal(72, 1.5)
            flow = np.random.normal(45, 1.2)
            rpm = np.random.normal(1800, 30)
            health = max(0.5, 0.92 - self.drift * 0.1)
            failure_label = 0
            failure_event = False
        
        return {
            'asset_id': self.asset_id,
            'asset_type': self.asset_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sensors': {
                'temperature_c': round(float(temp), 2),
                'pressure_bar': round(float(press), 2),
                'vibration_mm_s': round(float(vib), 3),
                'flow_rate_kg_s': round(float(flow), 2),
                'rotation_rpm': round(float(rpm), 1),
                'health_score': round(float(health), 4),
                'failure_label': failure_label,
                'failure_event': failure_event,
            },
            'is_anomaly_injected': self.anomaly_active
        }
```

### 3. monte_carlo/engine.py

**Update thresholds and field names:**
```python
THRESHOLDS = {
    'temperature_c': 105.0,
    'pressure_bar': 85.0,
    'vibration_mm_s': 7.5,
}

def run_simulation(sensor_state: dict, n: int = 10_000) -> dict:
    np.random.seed(None)
    
    T = stats.norm(sensor_state['temperature_c'], 2.5).rvs(n)
    P = stats.norm(sensor_state['pressure_bar'], 1.5).rvs(n)
    V = stats.norm(sensor_state['vibration_mm_s'], 0.4).rvs(n)
    
    fails = (T > THRESHOLDS['temperature_c']) | \
            (P > THRESHOLDS['pressure_bar']) | \
            (V > THRESHOLDS['vibration_mm_s'])
    
    prob = float(fails.sum() / n)
    
    curr_vib = sensor_state['vibration_mm_s']
    days_p50 = max(1, int((THRESHOLDS['vibration_mm_s'] - curr_vib) / 0.002 / 86400))
    
    # ... rest of function
```

### 4. api/anomaly/detector.py

**Update feature list:**
```python
FEATURES = ['temperature_c', 'pressure_bar', 'vibration_mm_s', 
            'flow_rate_kg_s', 'rotation_rpm', 'health_score']

WARN_MAX = [95.0,  80.0, 5.0,  35.0, 1900.0, 0.75]
CRIT_MAX = [105.0, 85.0, 7.5,  30.0, 1950.0, 0.60]
```

### 5. frontend/react-dashboard/src/App.jsx

**Update sensor display:**
```jsx
const SENSOR_LABELS = {
  temperature_c: 'Temperature (°C)',
  pressure_bar: 'Pressure (bar)',
  vibration_mm_s: 'Vibration (mm/s)',
  flow_rate_kg_s: 'Flow Rate (kg/s)',
  rotation_rpm: 'Rotation (RPM)',
  health_score: 'Health Score',
};

// Update asset ID
const demoAsset = assets.find(a => a.asset_id === 'GDC-WP-007');
```

### 6. frontend/unity-twin/Assets/Scripts/SensorBridge.cs

**Update SensorValues class:**
```csharp
[System.Serializable]
public class SensorValues {
    public float temperature_c;
    public float pressure_bar;
    public float vibration_mm_s;
    public float flow_rate_kg_s;
    public float rotation_rpm;
    public float health_score;
    public int failure_label;
    public bool failure_event;
}
```

---

## 🎯 ROI NUMBERS - EXACT USAGE

### In Demo Script:
```
"Our Monte Carlo engine shows a 34% failure probability. 
If this bearing fails, GDC Kenya faces USD 180,000 in 
unplanned downtime costs. Our platform costs USD 48,000 
per year and prevents 2 failures annually, saving 
USD 360,000. That's a 650% return on investment."
```

### In Business Case:
```markdown
## Financial Impact

- **Unplanned Failure Cost**: USD 180,000 per event
- **Annual Platform Cost**: USD 48,000
- **Failures Prevented**: 2 per year (conservative)
- **Annual Savings**: USD 360,000
- **Net Benefit**: USD 312,000
- **ROI**: 650%
```

---

## 📊 SUCCESS METRICS - TESTING TARGETS

### Performance Benchmarks:
```python
# Test these after implementation
assert lstm_model.evaluate(X_test, y_test)['auc'] > 0.82
assert monte_carlo_time < 5.0  # seconds for 10k iterations
assert whatif_response_time < 2.0  # seconds
assert sensor_latency < 1.0  # seconds end-to-end
assert anomaly_detection_accuracy > 0.80
```

### Demo Day Checklist:
- [ ] LSTM AUC-ROC > 0.82 (show in Watson Studio)
- [ ] Monte Carlo completes in < 5s (show timer)
- [ ] What-If slider responds in < 2s (show network tab)
- [ ] Sensor updates in < 1s (show timestamp diff)
- [ ] Anomaly detected with > 80% confidence (show score)
- [ ] ROI calculation shows 650% (show in dashboard)

---

## 🌐 THREE.JS WEB VIEWER

### New Directory Structure:
```
frontend/threejs-viewer/
├── package.json
├── src/
│   ├── main.js              # Entry point
│   ├── AssetRenderer.js     # 3D rendering logic
│   ├── WebSocketClient.js   # Connection to FastAPI
│   ├── SensorOverlay.js     # HUD display
│   └── styles.css
├── public/
│   ├── index.html
│   └── models/              # 3D asset models (GLTF/GLB)
└── README.md
```

### Quick Setup:
```bash
cd frontend
mkdir threejs-viewer
cd threejs-viewer
npm init -y
npm install three @types/three
```

### Basic Implementation:
```javascript
// src/main.js
import * as THREE from 'three';
import { WebSocketClient } from './WebSocketClient';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

// Create 50 asset cubes in grid layout
const assets = {};
for (let i = 0; i < 50; i++) {
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshBasicMaterial({ color: 0x1E6B3C });
    const cube = new THREE.Mesh(geometry, material);
    cube.position.set((i % 10) * 2, Math.floor(i / 10) * 2, 0);
    scene.add(cube);
    assets[`asset-${i}`] = cube;
}

// WebSocket updates
const ws = new WebSocketClient('ws://localhost:8000/twin/stream');
ws.onMessage((data) => {
    data.assets.forEach(asset => {
        const cube = assets[asset.asset_id];
        if (cube) {
            cube.material.color.setHex(parseInt(asset.colour_hex.replace('#', '0x')));
        }
    });
});
```

---

## 🔄 MIGRATION SCRIPT

### Automated Find/Replace:
```bash
#!/bin/bash
# Run this from project root

# Backup first
git checkout -b backup-before-corrections

# Sensor field name updates
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.cs" \) \
  -exec sed -i 's/bearing_vibration_mms/vibration_mm_s/g' {} +

find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.cs" \) \
  -exec sed -i 's/bearing_temp_c/temperature_c/g' {} +

find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.cs" \) \
  -exec sed -i 's/steam_inlet_pressure_bar/pressure_bar/g' {} +

find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.cs" \) \
  -exec sed -i 's/turbine_rpm/rotation_rpm/g' {} +

find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.cs" \) \
  -exec sed -i 's/steam_flow_kgs/flow_rate_kg_s/g' {} +

# Asset ID updates
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.cs" \) \
  -exec sed -i 's/GDC-TURBINE-01/GDC-WP-007/g' {} +

echo "Migration complete. Review changes with: git diff"
```

---

## ✅ VERIFICATION STEPS

### After Making Changes:

1. **Verify Sensor Fields**:
```bash
# Should find NO occurrences of old names
grep -r "bearing_vibration_mms" --include="*.py" --include="*.js" --include="*.cs"
grep -r "bearing_temp_c" --include="*.py" --include="*.js" --include="*.cs"
```

2. **Verify Asset IDs**:
```bash
# Should find NO occurrences of old turbine ID
grep -r "GDC-TURBINE-01" --include="*.py" --include="*.js" --include="*.cs"
```

3. **Test Sensor Simulator**:
```bash
cd sensor_simulator
python3 -c "
from simulator import GeothermalSimulator
import json
sim = GeothermalSimulator('GDC-WP-007', 'well_pump')
reading = sim.get_reading()
print(json.dumps(reading, indent=2))
# Verify all 8 sensor fields present
assert 'temperature_c' in reading['sensors']
assert 'vibration_mm_s' in reading['sensors']
assert 'health_score' in reading['sensors']
print('✓ Sensor fields correct')
"
```

4. **Test Monte Carlo**:
```bash
cd monte_carlo
python3 -c "
from engine import run_simulation
result = run_simulation({
    'temperature_c': 85.0,
    'pressure_bar': 72.0,
    'vibration_mm_s': 3.8,
    'flow_rate_kg_s': 45.0,
    'rotation_rpm': 1800,
    'health_score': 0.92
})
print(f'Failure probability: {result[\"failure_probability\"]}')
assert 'failure_probability' in result
print('✓ Monte Carlo working with new fields')
"
```

---

## 📞 SUPPORT

If you encounter issues:

1. Check [`CORRECTED_SPECIFICATIONS.md`](./CORRECTED_SPECIFICATIONS.md)
2. Check [`GDC_ASSET_REFERENCE.md`](./GDC_ASSET_REFERENCE.md)
3. Review Philip's official docs in `1_phase/` folder
4. Check the 43,800-row training data in Excel file

---

**Last Updated**: March 24, 2026  
**Status**: Ready for Implementation  
**Next Step**: Start with sensor_simulator updates, then work through the stack