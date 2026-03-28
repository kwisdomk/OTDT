# GDC Plant Twin - Unity C# Scripts

**Project:** OT Digital Twin — Monte Carlo Industrial Digital Twin Platform  
**Client:** GDC Kenya (Geothermal Development Company)  
**Partner:** i3 Technologies Ltd — IBM Silver Partner CEID 7sq30  
**Build Guide:** v1.0 - Step 3: Unity XR 3D Model Construction (Lines 207-238)  
**Demo Date:** March 30-31, 2026

---

## 📋 Overview

This Unity project provides real-time 3D visualization of the GDC geothermal plant digital twin. It connects to the FastAPI backend via WebSocket to receive live sensor data and predictive analytics, displaying asset health through dynamic colour coding and an interactive HUD.

---

## 🎯 Core Scripts

### 1. **AssetState.cs**
Data model for asset state from the digital twin API.

**Purpose:**
- Defines the structure for asset data received from WebSocket
- Contains sensor readings, failure predictions, and maintenance recommendations

**Key Classes:**
- `AssetState` - Main asset state container
- `SensorData` - Sensor readings (temperature, pressure, vibration, flow, rotation)
- `TwinStreamMessage` - WebSocket message wrapper

---

### 2. **MainThreadDispatcher.cs**
Handles execution of callbacks on Unity's main thread.

**Purpose:**
- WebSocket callbacks run on background threads
- Unity objects can only be modified on the main thread
- This dispatcher queues actions for safe execution

**Usage:**
```csharp
MainThreadDispatcher.Enqueue(() => {
    // Code that modifies Unity objects
    transform.position = newPosition;
});
```

**Features:**
- Singleton pattern
- Thread-safe queue
- Automatic error handling
- Persists across scene loads

---

### 3. **SensorBridge.cs**
WebSocket client for real-time sensor data from FastAPI backend.

**Purpose:**
- Connects to `ws://localhost:8000/twin/stream`
- Receives real-time asset state updates
- Broadcasts updates to other Unity components
- Handles connection failures with automatic reconnection

**Configuration:**
```csharp
[SerializeField] private string webSocketUrl = "ws://localhost:8000/twin/stream";
[SerializeField] private float reconnectDelay = 5f;
[SerializeField] private int maxReconnectAttempts = 10;
```

**Environment Variable Override:**
Set `TWIN_WEBSOCKET_URL` to override the default WebSocket URL.

**Events:**
- `OnAssetStateUpdated(string assetId, AssetState state)` - Fired when asset data updates
- `OnConnectionStatusChanged(bool connected)` - Fired on connection status change

**Static API:**
```csharp
// Get asset state by ID
AssetState state = SensorBridge.GetAssetState("GDC-WP-007");

// Check if asset exists
bool exists = SensorBridge.HasAssetState("GDC-WP-007");

// Access all states
Dictionary<string, AssetState> states = SensorBridge.LatestAssetStates;
```

**Reconnection Logic:**
- Automatically reconnects on connection loss
- Exponential backoff with configurable delay
- Maximum retry attempts to prevent infinite loops
- Manual reconnection via `ManualReconnect()` method

---

### 4. **ColourController.cs**
Controls material colour based on asset health status.

**Purpose:**
- Attach to each asset GameObject in the scene
- Listens for state updates from SensorBridge
- Applies colour from `colour_hex` to material
- Smooth colour transitions

**Setup:**
1. Attach to asset GameObject
2. Set `assetId` to match API asset ID (e.g., "GDC-WP-007")
3. If `assetId` is empty, uses GameObject name

**Colour Mapping:**
- **Green (#00FF00)** - NORMAL status
- **Orange (#FFA500)** - WARNING status
- **Red (#FF0000)** - CRITICAL status
- **Gray (#808080)** - UNKNOWN/Disconnected

**Features:**
- Smooth colour transitions (configurable speed)
- Optional emission for glowing effect
- Fallback colours if hex parsing fails
- MaterialPropertyBlock for performance (no material instantiation)

**Configuration:**
```csharp
[SerializeField] private float colorTransitionSpeed = 2f;
[SerializeField] private bool useEmission = true;
[SerializeField] private float emissionIntensity = 0.5f;
```

---

### 5. **HUDController.cs**
UI controller for displaying asset health and sensor data.

**Purpose:**
- Shows selected asset information
- Displays failure probability and predictions
- Shows real-time sensor readings
- Indicates connection status

**UI Elements Required:**
- Asset ID and name text
- Status text with colour coding
- Failure probability bar and percentage
- Days to failure (P50) text
- Recommended action text
- Work order panel (optional)
- Sensor readings panel
- Connection status indicator
- Synthetic data disclaimer

**Usage:**
```csharp
// Select an asset to display
hudController.SelectAsset("GDC-WP-007");

// Deselect and hide HUD
hudController.DeselectAsset();

// Check if asset is selected
bool selected = hudController.IsAssetSelected();
```

**Status Colours:**
- **NORMAL** - Green
- **WARNING** - Orange
- **CRITICAL** - Red

**Action Colours:**
- **MONITOR** - Green
- **SCHEDULE_MAINTENANCE** - Orange
- **URGENT** - Red

**Synthetic Data Warning:**
Displays "⚠️ DEMO MODE - Synthetic Data for Demonstration Purposes" when enabled.

---

### 6. **CameraController.cs**
Orbital camera controller for 3D scene navigation.

**Purpose:**
- Mouse drag (left-click) to rotate around scene
- Scroll wheel to zoom in/out
- Right-click to pan
- Smooth camera movement

**Controls:**
- **Left Mouse Drag** - Rotate camera
- **Right Mouse Drag** - Pan camera
- **Scroll Wheel** - Zoom in/out
- **F Key** - Focus on target
- **Home Key** - Reset camera to initial position

**Configuration:**
```csharp
[SerializeField] private Transform target; // Optional orbit target
[SerializeField] private float distance = 20f;
[SerializeField] private float rotationSpeed = 2f;
[SerializeField] private float zoomSpeed = 5f;
[SerializeField] private float panSpeed = 1f;
```

**Features:**
- Smooth rotation, zoom, and pan
- Configurable speed and limits
- Optional target following
- Keyboard shortcuts for quick navigation
- Vertical angle clamping to prevent flipping

**API:**
```csharp
// Set camera target
cameraController.SetTarget(assetTransform);

// Set distance
cameraController.SetDistance(30f);

// Look at position
cameraController.LookAt(Vector3.zero);

// Reset camera
cameraController.ResetCamera();

// Enable/disable controls
cameraController.SetControlsEnabled(rotation: true, zoom: true, pan: true);
```

---

## 🔧 Dependencies

### Required Unity Packages

Install via Unity Package Manager:

1. **NativeWebSocket**
   - URL: `https://github.com/endel/NativeWebSocket.git`
   - Purpose: WebSocket client for real-time communication
   - Installation: Package Manager → Add package from git URL

2. **Newtonsoft.Json**
   - Package: `com.unity.nuget.newtonsoft-json`
   - Purpose: JSON parsing for WebSocket messages
   - Installation: Package Manager → Search "Newtonsoft.Json"

### Alternative: Unity's JsonUtility

If Newtonsoft.Json is unavailable, you can use Unity's built-in `JsonUtility`:

```csharp
// Replace in SensorBridge.cs
TwinStreamMessage message = JsonUtility.FromJson<TwinStreamMessage>(json);
```

**Note:** JsonUtility requires `[Serializable]` attributes on all classes (already added).

---

## 🏗️ Scene Setup

### 1. Scene Hierarchy

Create the following structure:

```
GDC_Plant/
├── WellPumps/
│   ├── GDC-WP-001
│   ├── GDC-WP-002
│   ├── ...
│   └── GDC-WP-020
├── HeatExchangers/
│   ├── GDC-HX-001
│   ├── ...
│   └── GDC-HX-010
├── Turbines/
│   ├── GDC-TU-001
│   ├── ...
│   └── GDC-TU-010
└── ProductionPipes/
    ├── GDC-PP-001
    ├── ...
    └── GDC-PP-010
```

### 2. Asset GameObject Setup

For each asset (e.g., GDC-WP-007):

1. **Name:** Must match `asset_id` from API (e.g., "GDC-WP-007")
2. **Components:**
   - MeshRenderer (or any Renderer component)
   - ColourController script
3. **ColourController Settings:**
   - Asset ID: Leave empty to use GameObject name
   - Color Transition Speed: 2.0
   - Use Emission: ✓ (optional)

### 3. Main Camera Setup

1. **Components:**
   - Camera
   - CameraController script
2. **CameraController Settings:**
   - Target: Leave empty or set to scene center
   - Distance: 20
   - Rotation Speed: 2
   - Zoom Speed: 5
   - Pan Speed: 1

### 4. SensorBridge Setup

Create an empty GameObject named "SensorBridge":

1. **Components:**
   - SensorBridge script
2. **Settings:**
   - WebSocket URL: `ws://localhost:8000/twin/stream`
   - Reconnect Delay: 5
   - Max Reconnect Attempts: 10

### 5. HUD Canvas Setup

Create a Canvas with:

1. **Canvas Settings:**
   - Render Mode: Screen Space - Overlay
   - Canvas Scaler: Scale with Screen Size
2. **UI Elements:**
   - Asset info panel (top-left)
   - Sensor readings panel (bottom-left)
   - Connection status indicator (top-right)
   - Disclaimer text (bottom-center)
3. **HUDController:**
   - Attach to Canvas
   - Assign all UI element references

---

## 🚀 Quick Start

### 1. Start FastAPI Backend

```bash
cd otdt/OTDT
uvicorn api.main:app --reload
```

Verify endpoints:
- API: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/twin/stream

### 2. Open Unity Project

```bash
cd otdt/OTDT/unity/GDC_Plant_Twin
# Open in Unity Editor
```

### 3. Install Dependencies

1. Open Package Manager (Window → Package Manager)
2. Add NativeWebSocket from git URL
3. Add Newtonsoft.Json from Unity Registry

### 4. Setup Scene

1. Create scene hierarchy (see above)
2. Add 50 asset GameObjects with correct names
3. Attach ColourController to each asset
4. Setup Camera with CameraController
5. Create SensorBridge GameObject
6. Setup HUD Canvas with HUDController

### 5. Run

1. Press Play in Unity Editor
2. Check Console for connection status
3. Assets should start changing colours based on API data
4. Click assets to view details in HUD

---

## 🎮 Demo Flow

### Expected Behavior

1. **Startup:**
   - SensorBridge connects to WebSocket
   - Console shows: "✅ WebSocket connected successfully"
   - Connection indicator turns green

2. **Real-Time Updates:**
   - Assets change colour every few seconds
   - Green = Normal, Orange = Warning, Red = Critical
   - Console logs: "Updated X assets at [timestamp]"

3. **Asset Selection:**
   - Click an asset GameObject
   - HUD displays:
     - Asset ID and name
     - Failure probability (percentage and bar)
     - Days to failure (P50)
     - Recommended action
     - Sensor readings
     - Work order (if active)

4. **Camera Navigation:**
   - Left-drag to rotate
   - Scroll to zoom
   - Right-drag to pan
   - Press F to focus
   - Press Home to reset

---

## 🐛 Troubleshooting

### WebSocket Connection Failed

**Symptoms:**
- Console: "Connection failed: [error]"
- Assets remain gray
- Connection indicator red

**Solutions:**
1. Verify FastAPI is running: `curl http://localhost:8000/health`
2. Check WebSocket URL in SensorBridge
3. Check firewall settings
4. Try manual reconnect: `sensorBridge.ManualReconnect()`

### Assets Not Changing Colour

**Symptoms:**
- WebSocket connected
- No colour updates

**Solutions:**
1. Verify asset GameObject names match API asset IDs
2. Check ColourController is attached to assets
3. Verify assets have Renderer component
4. Check Console for parsing errors

### HUD Not Updating

**Symptoms:**
- Assets change colour
- HUD shows old/no data

**Solutions:**
1. Verify HUDController is attached to Canvas
2. Check all UI element references are assigned
3. Verify asset selection is working
4. Check Console for errors

### Performance Issues

**Symptoms:**
- Low frame rate
- Stuttering

**Solutions:**
1. Reduce number of assets
2. Disable emission on ColourController
3. Increase color transition speed
4. Use LOD (Level of Detail) for asset meshes
5. Optimize materials (use Standard shader)

---

## 📊 Asset Naming Convention

All GameObjects must match these asset IDs:

### Well Pumps (20)
- GDC-WP-001 through GDC-WP-020

### Heat Exchangers (10)
- GDC-HX-001 through GDC-HX-010

### Turbines (10)
- GDC-TU-001 through GDC-TU-010

### Production Pipes (10)
- GDC-PP-001 through GDC-PP-010

**Total:** 50 assets

---

## 🔌 API Integration

### WebSocket Endpoint

**URL:** `ws://localhost:8000/twin/stream`

**Message Format:**
```json
{
  "timestamp": "2026-03-28T12:00:00Z",
  "assets": [
    {
      "asset_id": "GDC-WP-007",
      "asset_label": "Well Pump 7",
      "status": "NORMAL",
      "colour_hex": "#00FF00",
      "failure_probability": 0.34,
      "days_to_failure_p50": 45,
      "recommended_action": "MONITOR",
      "work_order_id": null,
      "sensors": {
        "temperature_c": 85.3,
        "pressure_bar": 46.2,
        "vibration_mm_s": 2.1,
        "flow_rate_kg_s": 125.4,
        "rotation_rpm": 3580
      }
    }
  ]
}
```

### REST Endpoints (Optional)

- `GET /api/assets` - List all assets
- `GET /api/twins/{id}/sensors/latest` - Latest sensor data
- `GET /health` - Health check

---

## 📝 Build Guide Compliance

This implementation follows **Build Guide v1.0 - Step 3: Unity XR 3D Model Construction (Lines 207-238)**:

✅ WebSocket connection to FastAPI backend  
✅ Real-time sensor data visualization  
✅ Colour-coded asset health status  
✅ Interactive HUD with failure predictions  
✅ Orbital camera navigation  
✅ 50 GDC assets with correct naming  
✅ Synthetic data disclaimer  
✅ Error handling and reconnection logic  

---

## 🎯 Demo Checklist

Before the demo on March 30-31:

- [ ] FastAPI backend running and accessible
- [ ] All 50 assets created with correct names
- [ ] ColourController attached to all assets
- [ ] SensorBridge connected and receiving data
- [ ] HUD displaying asset information correctly
- [ ] Camera controls working smoothly
- [ ] Synthetic data disclaimer visible
- [ ] Connection status indicator working
- [ ] Test asset selection and HUD updates
- [ ] Verify colour changes on status updates
- [ ] Test reconnection on backend restart

---

## 📞 Support

**Project Lead:** [Your Name]  
**Partner:** i3 Technologies Ltd  
**Client:** GDC Kenya  

For technical issues, check:
1. Unity Console for errors
2. FastAPI logs: `uvicorn api.main:app --reload`
3. Browser DevTools (if using WebGL build)

---

## 📄 License

Proprietary - GDC Kenya & i3 Technologies Ltd  
IBM Silver Partner CEID 7sq30

---

**Last Updated:** March 28, 2026  
**Version:** 1.0  
**Status:** Ready for Demo