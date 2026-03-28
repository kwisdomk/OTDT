// unity/GDC_Plant_Twin/Assets/Scripts/AssetSelector.cs
// Handles asset selection via mouse clicks using raycasting
// Integrates with HUDController to display selected asset information
// Build Guide v1.0 - Step 3: Unity XR 3D Model Construction (Lines 207-238)

using UnityEngine;

namespace GDCPlantTwin
{
    /// <summary>
    /// Manages asset selection through mouse clicks
    /// Uses raycasting to detect clicked assets and updates HUD
    /// </summary>
    public class AssetSelector : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private HUDController hudController;
        [SerializeField] private Camera mainCamera;
        
        [Header("Selection Settings")]
        [SerializeField] private LayerMask selectableLayer = -1; // All layers
        [SerializeField] private float maxRayDistance = 1000f;
        [SerializeField] private KeyCode selectKey = KeyCode.Mouse0; // Left mouse button
        
        [Header("Visual Feedback")]
        [SerializeField] private bool showSelectionOutline = true;
        [SerializeField] private Color selectionColor = Color.yellow;
        [SerializeField] private float outlineWidth = 0.1f;
        
        [Header("Status")]
        [SerializeField] private GameObject selectedAsset;
        [SerializeField] private string selectedAssetId;
        
        private Renderer selectedRenderer;
        private MaterialPropertyBlock originalPropertyBlock;
        private MaterialPropertyBlock selectionPropertyBlock;
        
        private static readonly int OutlineColorId = Shader.PropertyToID("_OutlineColor");
        private static readonly int OutlineWidthId = Shader.PropertyToID("_OutlineWidth");

        void Awake()
        {
            // Get main camera if not assigned
            if (mainCamera == null)
            {
                mainCamera = Camera.main;
                if (mainCamera == null)
                {
                    Debug.LogError("[AssetSelector] No main camera found!");
                }
            }
            
            // Get HUD controller if not assigned
            if (hudController == null)
            {
                hudController = FindObjectOfType<HUDController>();
                if (hudController == null)
                {
                    Debug.LogWarning("[AssetSelector] No HUDController found in scene");
                }
            }
            
            originalPropertyBlock = new MaterialPropertyBlock();
            selectionPropertyBlock = new MaterialPropertyBlock();
        }

        void Update()
        {
            HandleSelection();
            
            // Deselect with Escape key
            if (Input.GetKeyDown(KeyCode.Escape) && selectedAsset != null)
            {
                DeselectAsset();
            }
        }

        void HandleSelection()
        {
            // Check for mouse click
            if (Input.GetKeyDown(selectKey))
            {
                Ray ray = mainCamera.ScreenPointToRay(Input.mousePosition);
                RaycastHit hit;
                
                if (Physics.Raycast(ray, out hit, maxRayDistance, selectableLayer))
                {
                    GameObject hitObject = hit.collider.gameObject;
                    
                    // Check if the hit object has a ColourController (is an asset)
                    ColourController colourController = hitObject.GetComponent<ColourController>();
                    
                    if (colourController != null)
                    {
                        SelectAsset(hitObject, colourController.GetAssetId());
                    }
                    else
                    {
                        // Try parent object
                        colourController = hitObject.GetComponentInParent<ColourController>();
                        if (colourController != null)
                        {
                            SelectAsset(colourController.gameObject, colourController.GetAssetId());
                        }
                        else
                        {
                            Debug.Log($"[AssetSelector] Clicked object '{hitObject.name}' is not a selectable asset");
                        }
                    }
                }
            }
        }

        void SelectAsset(GameObject asset, string assetId)
        {
            // Deselect previous asset
            if (selectedAsset != null && selectedAsset != asset)
            {
                ClearSelection();
            }
            
            // Select new asset
            selectedAsset = asset;
            selectedAssetId = assetId;
            
            Debug.Log($"[AssetSelector] Selected asset: {assetId}");
            
            // Apply visual feedback
            if (showSelectionOutline)
            {
                ApplySelectionOutline();
            }
            
            // Update HUD
            if (hudController != null)
            {
                hudController.SelectAsset(assetId);
            }
            else
            {
                Debug.LogWarning("[AssetSelector] HUDController not available");
            }
        }

        void DeselectAsset()
        {
            if (selectedAsset == null) return;
            
            Debug.Log($"[AssetSelector] Deselected asset: {selectedAssetId}");
            
            ClearSelection();
            
            selectedAsset = null;
            selectedAssetId = null;
            
            // Clear HUD
            if (hudController != null)
            {
                hudController.DeselectAsset();
            }
        }

        void ApplySelectionOutline()
        {
            if (selectedAsset == null) return;
            
            selectedRenderer = selectedAsset.GetComponent<Renderer>();
            if (selectedRenderer == null) return;
            
            // Store original property block
            selectedRenderer.GetPropertyBlock(originalPropertyBlock);
            
            // Create selection property block
            selectedRenderer.GetPropertyBlock(selectionPropertyBlock);
            
            // Note: This requires a shader that supports outline properties
            // For basic highlighting, you can modify the emission color instead
            if (selectionPropertyBlock != null)
            {
                // Try to set outline properties (if shader supports it)
                selectionPropertyBlock.SetColor(OutlineColorId, selectionColor);
                selectionPropertyBlock.SetFloat(OutlineWidthId, outlineWidth);
                
                selectedRenderer.SetPropertyBlock(selectionPropertyBlock);
            }
        }

        void ClearSelection()
        {
            if (selectedRenderer != null && originalPropertyBlock != null)
            {
                // Restore original property block
                selectedRenderer.SetPropertyBlock(originalPropertyBlock);
                selectedRenderer = null;
            }
        }

        // Public API
        public GameObject GetSelectedAsset()
        {
            return selectedAsset;
        }

        public string GetSelectedAssetId()
        {
            return selectedAssetId;
        }

        public bool HasSelection()
        {
            return selectedAsset != null;
        }

        public void ClearCurrentSelection()
        {
            DeselectAsset();
        }

        // Programmatic selection
        public void SelectAssetById(string assetId)
        {
            // Find asset by ID
            ColourController[] controllers = FindObjectsOfType<ColourController>();
            
            foreach (var controller in controllers)
            {
                if (controller.GetAssetId() == assetId)
                {
                    SelectAsset(controller.gameObject, assetId);
                    return;
                }
            }
            
            Debug.LogWarning($"[AssetSelector] Asset with ID '{assetId}' not found");
        }

        // Draw selection ray in editor
        void OnDrawGizmos()
        {
            if (mainCamera == null || !Application.isPlaying) return;
            
            Ray ray = mainCamera.ScreenPointToRay(Input.mousePosition);
            Gizmos.color = Color.yellow;
            Gizmos.DrawRay(ray.origin, ray.direction * maxRayDistance);
            
            // Draw selected asset
            if (selectedAsset != null)
            {
                Gizmos.color = selectionColor;
                Gizmos.DrawWireSphere(selectedAsset.transform.position, 1f);
            }
        }
    }
}

// Made with Bob
