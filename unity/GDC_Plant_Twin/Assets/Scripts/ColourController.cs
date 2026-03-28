// unity/GDC_Plant_Twin/Assets/Scripts/ColourController.cs
// Controls material colour based on asset health status
// Attach to each asset GameObject in the scene
// Build Guide v1.0 - Step 3: Unity XR 3D Model Construction (Lines 207-238)

using System;
using UnityEngine;

namespace GDCPlantTwin
{
    /// <summary>
    /// Manages visual representation of asset health through colour changes
    /// Subscribes to SensorBridge updates and applies colours to materials
    /// </summary>
    [RequireComponent(typeof(Renderer))]
    public class ColourController : MonoBehaviour
    {
        [Header("Asset Configuration")]
        [SerializeField] private string assetId;
        [Tooltip("If empty, will use GameObject name as asset ID")]
        
        [Header("Visual Settings")]
        [SerializeField] private float colorTransitionSpeed = 2f;
        [SerializeField] private bool useEmission = true;
        [SerializeField] private float emissionIntensity = 0.5f;
        
        [Header("Fallback Colours")]
        [SerializeField] private Color normalColor = new Color(0f, 1f, 0f); // Green
        [SerializeField] private Color warningColor = new Color(1f, 0.65f, 0f); // Orange
        [SerializeField] private Color criticalColor = new Color(1f, 0f, 0f); // Red
        [SerializeField] private Color unknownColor = new Color(0.5f, 0.5f, 0.5f); // Gray
        
        [Header("Status")]
        [SerializeField] private string currentStatus = "UNKNOWN";
        [SerializeField] private bool isConnected = false;
        
        private Renderer objectRenderer;
        private MaterialPropertyBlock propertyBlock;
        private Color targetColor;
        private Color currentColor;
        private bool hasReceivedData = false;
        
        // Material property IDs for performance
        private static readonly int ColorPropertyId = Shader.PropertyToID("_Color");
        private static readonly int EmissionColorPropertyId = Shader.PropertyToID("_EmissionColor");

        void Awake()
        {
            objectRenderer = GetComponent<Renderer>();
            propertyBlock = new MaterialPropertyBlock();
            
            // Use GameObject name as asset ID if not set
            if (string.IsNullOrEmpty(assetId))
            {
                assetId = gameObject.name;
                Debug.Log($"[ColourController] Using GameObject name as asset ID: {assetId}");
            }
            
            // Set initial color
            currentColor = unknownColor;
            targetColor = unknownColor;
            ApplyColorImmediate(unknownColor);
        }

        void OnEnable()
        {
            // Subscribe to asset state updates
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
            // Check if we already have state for this asset
            AssetState state = SensorBridge.GetAssetState(assetId);
            if (state != null)
            {
                UpdateFromAssetState(state);
            }
        }

        void Update()
        {
            // Smooth color transition
            if (Vector4.Distance(currentColor, targetColor) > 0.01f)
            {
                currentColor = Color.Lerp(currentColor, targetColor, Time.deltaTime * colorTransitionSpeed);
                ApplyColorImmediate(currentColor);
            }
        }

        void OnAssetStateUpdated(string updatedAssetId, AssetState state)
        {
            // Only process updates for this asset
            if (updatedAssetId == assetId)
            {
                UpdateFromAssetState(state);
            }
        }

        void OnConnectionStatusChanged(bool connected)
        {
            isConnected = connected;
            
            if (!connected && !hasReceivedData)
            {
                // Show disconnected state
                targetColor = unknownColor;
                currentStatus = "DISCONNECTED";
            }
        }

        void UpdateFromAssetState(AssetState state)
        {
            if (state == null) return;
            
            hasReceivedData = true;
            currentStatus = state.status;
            
            // Parse colour from hex if available
            if (!string.IsNullOrEmpty(state.colour_hex))
            {
                Color parsedColor;
                if (TryParseHexColor(state.colour_hex, out parsedColor))
                {
                    targetColor = parsedColor;
                }
                else
                {
                    // Fallback to status-based colour
                    targetColor = GetColorForStatus(state.status);
                }
            }
            else
            {
                // Use status-based colour
                targetColor = GetColorForStatus(state.status);
            }
        }

        Color GetColorForStatus(string status)
        {
            switch (status?.ToUpper())
            {
                case "NORMAL":
                    return normalColor;
                case "WARNING":
                    return warningColor;
                case "CRITICAL":
                    return criticalColor;
                default:
                    return unknownColor;
            }
        }

        bool TryParseHexColor(string hex, out Color color)
        {
            color = Color.white;
            
            try
            {
                // Remove # if present
                hex = hex.TrimStart('#');
                
                // Support both RGB and RGBA formats
                if (hex.Length == 6)
                {
                    hex += "FF"; // Add full alpha
                }
                
                if (hex.Length != 8)
                {
                    Debug.LogWarning($"[ColourController] Invalid hex color length: {hex}");
                    return false;
                }
                
                byte r = Convert.ToByte(hex.Substring(0, 2), 16);
                byte g = Convert.ToByte(hex.Substring(2, 2), 16);
                byte b = Convert.ToByte(hex.Substring(4, 2), 16);
                byte a = Convert.ToByte(hex.Substring(6, 2), 16);
                
                color = new Color32(r, g, b, a);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ColourController] Error parsing hex color '{hex}': {ex.Message}");
                return false;
            }
        }

        void ApplyColorImmediate(Color color)
        {
            if (objectRenderer == null) return;
            
            // Get current property block
            objectRenderer.GetPropertyBlock(propertyBlock);
            
            // Set base color
            propertyBlock.SetColor(ColorPropertyId, color);
            
            // Set emission if enabled
            if (useEmission)
            {
                Color emissionColor = color * emissionIntensity;
                propertyBlock.SetColor(EmissionColorPropertyId, emissionColor);
            }
            
            // Apply property block
            objectRenderer.SetPropertyBlock(propertyBlock);
        }

        // Public API for manual color updates
        public void SetColor(Color color)
        {
            targetColor = color;
        }

        public void SetColorHex(string hexColor)
        {
            Color color;
            if (TryParseHexColor(hexColor, out color))
            {
                targetColor = color;
            }
        }

        public string GetAssetId()
        {
            return assetId;
        }

        public string GetCurrentStatus()
        {
            return currentStatus;
        }

        // Editor helper
        void OnValidate()
        {
            if (string.IsNullOrEmpty(assetId) && gameObject != null)
            {
                assetId = gameObject.name;
            }
        }
    }
}

// Made with Bob
