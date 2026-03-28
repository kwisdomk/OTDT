// unity/GDC_Plant_Twin/Assets/Scripts/HUDController.cs
// UI controller for displaying asset health and sensor data
// Shows failure probability, recommended actions, and real-time sensor readings
// Build Guide v1.0 - Step 3: Unity XR 3D Model Construction (Lines 207-238)

using System;
using UnityEngine;
using UnityEngine.UI;

namespace GDCPlantTwin
{
    /// <summary>
    /// Manages the HUD overlay displaying selected asset information
    /// Updates in real-time based on SensorBridge data
    /// </summary>
    public class HUDController : MonoBehaviour
    {
        [Header("Asset Information")]
        [SerializeField] private Text assetIdText;
        [SerializeField] private Text assetNameText;
        [SerializeField] private Text statusText;
        
        [Header("Predictive Analytics")]
        [SerializeField] private Text probabilityText;
        [SerializeField] private Text probabilityPercentText;
        [SerializeField] private Image probabilityBar;
        [SerializeField] private Text daysToFailureText;
        [SerializeField] private Text recommendedActionText;
        
        [Header("Work Order")]
        [SerializeField] private GameObject workOrderPanel;
        [SerializeField] private Text workOrderIdText;
        [SerializeField] private Text workOrderStatusText;
        
        [Header("Sensor Readings")]
        [SerializeField] private GameObject sensorPanel;
        [SerializeField] private Text temperatureText;
        [SerializeField] private Text pressureText;
        [SerializeField] private Text vibrationText;
        [SerializeField] private Text flowRateText;
        [SerializeField] private Text rotationText;
        
        [Header("Connection Status")]
        [SerializeField] private GameObject connectionIndicator;
        [SerializeField] private Text connectionStatusText;
        [SerializeField] private Image connectionStatusImage;
        [SerializeField] private Color connectedColor = Color.green;
        [SerializeField] private Color disconnectedColor = Color.red;
        
        [Header("Disclaimer")]
        [SerializeField] private Text disclaimerText;
        
        [Header("Settings")]
        [SerializeField] private bool showSyntheticDataWarning = true;
        
        private string selectedAssetId;
        private AssetState currentAssetState;
        private bool isConnected = false;

        void Awake()
        {
            // Set synthetic data disclaimer
            if (disclaimerText != null && showSyntheticDataWarning)
            {
                disclaimerText.text = "⚠️ DEMO MODE - Synthetic Data for Demonstration Purposes";
            }
            
            // Hide panels initially
            if (sensorPanel != null) sensorPanel.SetActive(false);
            if (workOrderPanel != null) workOrderPanel.SetActive(false);
        }

        void OnEnable()
        {
            // Subscribe to events
            SensorBridge.OnAssetStateUpdated += OnAssetStateUpdated;
            SensorBridge.OnConnectionStatusChanged += OnConnectionStatusChanged;
        }

        void OnDisable()
        {
            // Unsubscribe from events
            SensorBridge.OnAssetStateUpdated -= OnAssetStateUpdated;
            SensorBridge.OnConnectionStatusChanged -= OnConnectionStatusChanged;
        }

        void Start()
        {
            // Initialize connection status
            UpdateConnectionStatus(false);
        }

        void OnAssetStateUpdated(string assetId, AssetState state)
        {
            // Update if this is the selected asset
            if (assetId == selectedAssetId)
            {
                currentAssetState = state;
                UpdateUI(state);
            }
        }

        void OnConnectionStatusChanged(bool connected)
        {
            isConnected = connected;
            UpdateConnectionStatus(connected);
        }

        /// <summary>
        /// Select an asset to display in the HUD
        /// </summary>
        public void SelectAsset(string assetId)
        {
            selectedAssetId = assetId;
            
            // Get current state from SensorBridge
            AssetState state = SensorBridge.GetAssetState(assetId);
            
            if (state != null)
            {
                currentAssetState = state;
                UpdateUI(state);
                
                // Show sensor panel
                if (sensorPanel != null) sensorPanel.SetActive(true);
            }
            else
            {
                // Asset not found - show placeholder
                ClearUI();
                if (assetIdText != null) assetIdText.text = $"Asset: {assetId}";
                if (assetNameText != null) assetNameText.text = "Waiting for data...";
            }
        }

        /// <summary>
        /// Deselect current asset and hide HUD
        /// </summary>
        public void DeselectAsset()
        {
            selectedAssetId = null;
            currentAssetState = null;
            ClearUI();
            
            if (sensorPanel != null) sensorPanel.SetActive(false);
            if (workOrderPanel != null) workOrderPanel.SetActive(false);
        }

        void UpdateUI(AssetState state)
        {
            if (state == null) return;
            
            // Asset Information
            if (assetIdText != null)
                assetIdText.text = $"Asset: {state.asset_id}";
            
            if (assetNameText != null)
                assetNameText.text = state.asset_label ?? state.asset_id;
            
            if (statusText != null)
            {
                statusText.text = $"Status: {state.status}";
                statusText.color = GetStatusColor(state.status);
            }
            
            // Predictive Analytics
            if (probabilityText != null)
                probabilityText.text = $"Failure Probability: {state.failure_probability:P1}";
            
            if (probabilityPercentText != null)
                probabilityPercentText.text = $"{state.failure_probability * 100:F1}%";
            
            if (probabilityBar != null)
            {
                probabilityBar.fillAmount = state.failure_probability;
                probabilityBar.color = GetProbabilityColor(state.failure_probability);
            }
            
            if (daysToFailureText != null)
                daysToFailureText.text = $"Days to Failure (P50): {state.days_to_failure_p50}";
            
            if (recommendedActionText != null)
            {
                recommendedActionText.text = $"Action: {FormatRecommendedAction(state.recommended_action)}";
                recommendedActionText.color = GetActionColor(state.recommended_action);
            }
            
            // Work Order
            if (!string.IsNullOrEmpty(state.work_order_id))
            {
                if (workOrderPanel != null) workOrderPanel.SetActive(true);
                if (workOrderIdText != null) workOrderIdText.text = $"WO: {state.work_order_id}";
                if (workOrderStatusText != null) workOrderStatusText.text = "Active";
            }
            else
            {
                if (workOrderPanel != null) workOrderPanel.SetActive(false);
            }
            
            // Sensor Readings
            if (state.sensors != null)
            {
                if (temperatureText != null)
                    temperatureText.text = $"Temperature: {state.sensors.temperature_c:F1}°C";
                
                if (pressureText != null)
                    pressureText.text = $"Pressure: {state.sensors.pressure_bar:F1} bar";
                
                if (vibrationText != null)
                    vibrationText.text = $"Vibration: {state.sensors.vibration_mm_s:F2} mm/s";
                
                if (flowRateText != null)
                    flowRateText.text = $"Flow Rate: {state.sensors.flow_rate_kg_s:F1} kg/s";
                
                if (rotationText != null)
                    rotationText.text = $"Rotation: {state.sensors.rotation_rpm:F0} RPM";
            }
        }

        void ClearUI()
        {
            if (assetIdText != null) assetIdText.text = "Asset: None";
            if (assetNameText != null) assetNameText.text = "Select an asset";
            if (statusText != null) statusText.text = "Status: -";
            if (probabilityText != null) probabilityText.text = "Failure Probability: -";
            if (probabilityPercentText != null) probabilityPercentText.text = "-";
            if (probabilityBar != null) probabilityBar.fillAmount = 0;
            if (daysToFailureText != null) daysToFailureText.text = "Days to Failure: -";
            if (recommendedActionText != null) recommendedActionText.text = "Action: -";
            
            if (temperatureText != null) temperatureText.text = "Temperature: -";
            if (pressureText != null) pressureText.text = "Pressure: -";
            if (vibrationText != null) vibrationText.text = "Vibration: -";
            if (flowRateText != null) flowRateText.text = "Flow Rate: -";
            if (rotationText != null) rotationText.text = "Rotation: -";
        }

        void UpdateConnectionStatus(bool connected)
        {
            if (connectionStatusText != null)
            {
                connectionStatusText.text = connected ? "Connected" : "Disconnected";
            }
            
            if (connectionStatusImage != null)
            {
                connectionStatusImage.color = connected ? connectedColor : disconnectedColor;
            }
            
            if (connectionIndicator != null)
            {
                connectionIndicator.SetActive(true);
            }
        }

        Color GetStatusColor(string status)
        {
            switch (status?.ToUpper())
            {
                case "NORMAL":
                    return Color.green;
                case "WARNING":
                    return new Color(1f, 0.65f, 0f); // Orange
                case "CRITICAL":
                    return Color.red;
                default:
                    return Color.gray;
            }
        }

        Color GetProbabilityColor(float probability)
        {
            if (probability < 0.3f)
                return Color.green;
            else if (probability < 0.7f)
                return new Color(1f, 0.65f, 0f); // Orange
            else
                return Color.red;
        }

        Color GetActionColor(string action)
        {
            switch (action?.ToUpper())
            {
                case "MONITOR":
                    return Color.green;
                case "SCHEDULE_MAINTENANCE":
                    return new Color(1f, 0.65f, 0f); // Orange
                case "URGENT":
                    return Color.red;
                default:
                    return Color.white;
            }
        }

        string FormatRecommendedAction(string action)
        {
            if (string.IsNullOrEmpty(action)) return "None";
            
            // Convert SCHEDULE_MAINTENANCE to "Schedule Maintenance"
            return action.Replace("_", " ")
                        .ToLower()
                        .Replace("monitor", "Monitor")
                        .Replace("schedule maintenance", "Schedule Maintenance")
                        .Replace("urgent", "URGENT");
        }

        // Public API for external scripts
        public string GetSelectedAssetId()
        {
            return selectedAssetId;
        }

        public AssetState GetCurrentAssetState()
        {
            return currentAssetState;
        }

        public bool IsAssetSelected()
        {
            return !string.IsNullOrEmpty(selectedAssetId);
        }
    }
}

// Made with Bob
