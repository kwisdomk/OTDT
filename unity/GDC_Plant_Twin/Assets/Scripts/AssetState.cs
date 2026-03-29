// unity/GDC_Plant_Twin/Assets/Scripts/AssetState.cs
// Data model for asset state from WebSocket stream
// Build Guide v1.0 - Step 3: Unity XR 3D Model Construction (Lines 207-238)

using System;
using System.Collections.Generic;


    /// <summary>
    /// Represents the real-time state of a GDC asset from the digital twin API
    /// </summary>
    [Serializable]
    public class AssetState
    {
        public string asset_id;
        public string asset_label;
        public string status; // NORMAL, WARNING, CRITICAL
        public string colour_hex; // e.g., "#00FF00"
        public float failure_probability; // 0.0 to 1.0
        public int days_to_failure_p50;
        public string recommended_action; // MONITOR, SCHEDULE_MAINTENANCE, URGENT
        public string work_order_id; // Optional - may be null
        public SensorData sensors;
        
        public AssetState()
        {
            sensors = new SensorData();
        }
    }

    /// <summary>
    /// Sensor readings for an asset
    /// </summary>
    [Serializable]
    public class SensorData
    {
        public float temperature_c;
        public float pressure_bar;
        public float vibration_mm_s;
        public float flow_rate_kg_s;
        public float rotation_rpm;
    }

    /// <summary>
    /// WebSocket message wrapper from /twin/stream endpoint
    /// </summary>
    [Serializable]
    public class TwinStreamMessage
    {
        public string timestamp;
        public List<AssetState> assets;
        
        public TwinStreamMessage()
        {
            assets = new List<AssetState>();
        }
    }


// Made with Bob

