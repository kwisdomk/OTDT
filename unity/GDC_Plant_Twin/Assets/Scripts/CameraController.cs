// unity/GDC_Plant_Twin/Assets/Scripts/CameraController.cs
// Orbital camera controller for 3D scene navigation
// Mouse drag to rotate, scroll to zoom, right-click to pan
// Build Guide v1.0 - Step 3: Unity XR 3D Model Construction (Lines 207-238)

using UnityEngine;


    /// <summary>
    /// Provides intuitive camera controls for navigating the 3D plant model
    /// Supports rotation, zoom, and panning
    /// </summary>
    public class CameraController : MonoBehaviour
    {
        [Header("Target")]
        [SerializeField] private Transform target;
        [Tooltip("If null, will orbit around world origin")]
        
        [Header("Distance")]
        [SerializeField] private float distance = 20f;
        [SerializeField] private float minDistance = 5f;
        [SerializeField] private float maxDistance = 100f;
        
        [Header("Rotation")]
        [SerializeField] private float rotationSpeed = 2f;
        [SerializeField] private float minVerticalAngle = -80f;
        [SerializeField] private float maxVerticalAngle = 80f;
        [SerializeField] private bool invertY = false;
        
        [Header("Zoom")]
        [SerializeField] private float zoomSpeed = 5f;
        [SerializeField] private float zoomSmoothTime = 0.1f;
        
        [Header("Pan")]
        [SerializeField] private float panSpeed = 1f;
        [SerializeField] private float panSmoothTime = 0.1f;
        
        [Header("Input")]
        [SerializeField] private KeyCode rotateButton = KeyCode.Mouse0; // Left mouse
        [SerializeField] private KeyCode panButton = KeyCode.Mouse2; // Right mouse
        [SerializeField] private bool allowRotation = true;
        [SerializeField] private bool allowZoom = true;
        [SerializeField] private bool allowPan = true;
        
        [Header("Smoothing")]
        [SerializeField] private bool smoothRotation = true;
        [SerializeField] private float rotationSmoothTime = 0.1f;
        
        // Internal state
        private float currentX = 0f;
        private float currentY = 20f;
        private float targetX = 0f;
        private float targetY = 20f;
        
        private float currentDistance;
        private float targetDistance;
        private float zoomVelocity;
        
        private Vector3 targetPosition;
        private Vector3 panVelocity;
        
        private Vector3 lastMousePosition;
        private bool isRotating = false;
        private bool isPanning = false;

        void Start()
        {
            // Initialize camera position
            if (target == null)
            {
                targetPosition = Vector3.zero;
            }
            else
            {
                targetPosition = target.position;
            }
            
            currentDistance = distance;
            targetDistance = distance;
            
            // Set initial rotation from current camera orientation
            Vector3 angles = transform.eulerAngles;
            currentX = angles.y;
            currentY = angles.x;
            targetX = currentX;
            targetY = currentY;
            
            UpdateCameraPosition();
        }

        void LateUpdate()
        {
            HandleInput();
            UpdateCameraPosition();
        }

        void HandleInput()
        {
            // Block input when mouse is over UI
            if (UnityEngine.EventSystems.EventSystem.current != null &&
                UnityEngine.EventSystems.EventSystem.current.IsPointerOverGameObject())
                return;
            
            // Rotation
            if (allowRotation && Input.GetKey(rotateButton))
            {
                if (!isRotating)
                {
                    lastMousePosition = Input.mousePosition;
                    isRotating = true;
                }
                
                Vector3 mouseDelta = Input.mousePosition - lastMousePosition;
                lastMousePosition = Input.mousePosition;
                
                float deltaX = mouseDelta.x * rotationSpeed;
                float deltaY = mouseDelta.y * rotationSpeed * (invertY ? 1f : -1f);
                
                targetX += deltaX;
                targetY += deltaY;
                
                // Clamp vertical rotation
                targetY = Mathf.Clamp(targetY, minVerticalAngle, maxVerticalAngle);
            }
            else
            {
                isRotating = false;
            }
            
            // Zoom
            if (allowZoom)
            {
                float scrollDelta = Input.GetAxis("Mouse ScrollWheel");
                if (Mathf.Abs(scrollDelta) > 0.01f)
                {
                    targetDistance -= scrollDelta * zoomSpeed;
                    targetDistance = Mathf.Clamp(targetDistance, minDistance, maxDistance);
                }
            }
            
            // Pan
            if (allowPan && Input.GetKey(panButton))
            {
                if (!isPanning)
                {
                    lastMousePosition = Input.mousePosition;
                    isPanning = true;
                }
                
                Vector3 mouseDelta = Input.mousePosition - lastMousePosition;
                lastMousePosition = Input.mousePosition;
                
                // Calculate pan direction in world space
                Vector3 right = transform.right;
                Vector3 up = transform.up;
                
                float panX = -mouseDelta.x * panSpeed * currentDistance * 0.001f;
                float panY = -mouseDelta.y * panSpeed * currentDistance * 0.001f;
                
                targetPosition += right * panX + up * panY;
            }
            else
            {
                isPanning = false;
            }
            
            // Keyboard shortcuts for quick navigation
            if (Input.GetKeyDown(KeyCode.F))
            {
                // Focus on target
                FocusOnTarget();
            }
            
            if (Input.GetKeyDown(KeyCode.Home))
            {
                // Reset camera to initial position
                ResetCamera();
            }
        }

        void UpdateCameraPosition()
        {
            // Smooth rotation
            if (smoothRotation)
            {
                currentX = Mathf.LerpAngle(currentX, targetX, rotationSmoothTime * 10f * Time.deltaTime);
                currentY = Mathf.Lerp(currentY, targetY, rotationSmoothTime * 10f * Time.deltaTime);
            }
            else
            {
                currentX = targetX;
                currentY = targetY;
            }
            
            // Smooth zoom
            currentDistance = Mathf.SmoothDamp(currentDistance, targetDistance, ref zoomVelocity, zoomSmoothTime);
            
            // Smooth pan (if target is not set)
            if (target == null)
            {
                targetPosition = Vector3.SmoothDamp(targetPosition, targetPosition, ref panVelocity, panSmoothTime);
            }
            else
            {
                targetPosition = target.position;
            }
            
            // Calculate camera position
            Quaternion rotation = Quaternion.Euler(currentY, currentX, 0);
            Vector3 direction = rotation * Vector3.back;
            Vector3 position = targetPosition + direction * currentDistance;
            
            // Apply to transform
            transform.position = position;
            transform.LookAt(targetPosition);
        }

        /// <summary>
        /// Focus camera on the target or origin
        /// </summary>
        public void FocusOnTarget()
        {
            if (target != null)
            {
                targetPosition = target.position;
            }
            else
            {
                targetPosition = Vector3.zero;
            }
            
            targetDistance = distance;
        }

        /// <summary>
        /// Reset camera to initial position and rotation
        /// </summary>
        public void ResetCamera()
        {
            targetX = 0f;
            targetY = 20f;
            targetDistance = distance;
            
            if (target != null)
            {
                targetPosition = target.position;
            }
            else
            {
                targetPosition = Vector3.zero;
            }
        }

        /// <summary>
        /// Set the camera target dynamically
        /// </summary>
        public void SetTarget(Transform newTarget)
        {
            target = newTarget;
            if (target != null)
            {
                targetPosition = target.position;
            }
        }

        /// <summary>
        /// Set camera distance
        /// </summary>
        public void SetDistance(float newDistance)
        {
            targetDistance = Mathf.Clamp(newDistance, minDistance, maxDistance);
        }

        /// <summary>
        /// Look at a specific position
        /// </summary>
        public void LookAt(Vector3 position)
        {
            targetPosition = position;
            
            // Calculate rotation to look at position
            Vector3 direction = position - transform.position;
            Quaternion rotation = Quaternion.LookRotation(direction);
            Vector3 angles = rotation.eulerAngles;
            
            targetX = angles.y;
            targetY = angles.x;
        }

        /// <summary>
        /// Enable or disable camera controls
        /// </summary>
        public void SetControlsEnabled(bool rotation, bool zoom, bool pan)
        {
            allowRotation = rotation;
            allowZoom = zoom;
            allowPan = pan;
        }

        // Gizmos for debugging
        void OnDrawGizmosSelected()
        {
            if (target != null)
            {
                Gizmos.color = Color.yellow;
                Gizmos.DrawWireSphere(target.position, 0.5f);
                Gizmos.DrawLine(transform.position, target.position);
            }
            else
            {
                Gizmos.color = Color.yellow;
                Gizmos.DrawWireSphere(targetPosition, 0.5f);
                Gizmos.DrawLine(transform.position, targetPosition);
            }
        }
    }


// Made with Bob

