// unity/GDC_Plant_Twin/Assets/Scripts/SensorBridge.cs
// WebSocket client for real-time sensor data from FastAPI backend
// Connects to ws://localhost:8000/twin/stream
// Build Guide v1.0 - Step 3: Unity XR 3D Model Construction (Lines 207-238)

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using NativeWebSocket;
using Newtonsoft.Json;

namespace GDCPlantTwin
{
    /// <summary>
    /// Manages WebSocket connection to the digital twin API
    /// Receives real-time asset state updates and broadcasts to Unity components
    /// </summary>
    public class SensorBridge : MonoBehaviour
    {
        [Header("WebSocket Configuration")]
        [SerializeField] private string webSocketUrl = "ws://localhost:8000/twin/stream";
        [SerializeField] private float reconnectDelay = 5f;
        [SerializeField] private int maxReconnectAttempts = 10;
        
        [Header("Status")]
        [SerializeField] private bool isConnected = false;
        [SerializeField] private int reconnectAttempts = 0;
        
        private WebSocket websocket;
        private bool shouldReconnect = true;
        
        // Static dictionary for asset states - accessible by other components
        public static Dictionary<string, AssetState> LatestAssetStates { get; private set; }
        
        // Event for asset state updates
        public static event Action<string, AssetState> OnAssetStateUpdated;
        public static event Action<bool> OnConnectionStatusChanged;
        
        void Awake()
        {
            LatestAssetStates = new Dictionary<string, AssetState>();
            
            // Ensure MainThreadDispatcher exists
            var dispatcher = MainThreadDispatcher.Instance;
        }

        async void Start()
        {
            Debug.Log("[SensorBridge] Starting WebSocket connection...");
            await Connect();
        }

        async Task Connect()
        {
            try
            {
                // Check for environment variable override
                string wsUrl = Environment.GetEnvironmentVariable("TWIN_WEBSOCKET_URL") ?? webSocketUrl;
                
                Debug.Log($"[SensorBridge] Connecting to {wsUrl}");
                
                websocket = new WebSocket(wsUrl);
                
                // Register event handlers
                websocket.OnOpen += OnWebSocketOpen;
                websocket.OnMessage += OnWebSocketMessage;
                websocket.OnError += OnWebSocketError;
                websocket.OnClose += OnWebSocketClose;
                
                // Connect
                await websocket.Connect();
            }
            catch (Exception ex)
            {
                Debug.LogError($"[SensorBridge] Connection failed: {ex.Message}");
                await ScheduleReconnect();
            }
        }

        void OnWebSocketOpen()
        {
            MainThreadDispatcher.Enqueue(() =>
            {
                isConnected = true;
                reconnectAttempts = 0;
                Debug.Log("[SensorBridge] ✅ WebSocket connected successfully");
                OnConnectionStatusChanged?.Invoke(true);
            });
        }

        void OnWebSocketMessage(byte[] data)
        {
            try
            {
                string json = System.Text.Encoding.UTF8.GetString(data);
                
                // Parse the message on background thread
                TwinStreamMessage message = JsonConvert.DeserializeObject<TwinStreamMessage>(json);
                
                if (message?.assets == null || message.assets.Count == 0)
                {
                    Debug.LogWarning("[SensorBridge] Received empty asset list");
                    return;
                }
                
                // Update state on main thread
                MainThreadDispatcher.Enqueue(() =>
                {
                    ProcessAssetUpdates(message);
                });
            }
            catch (Exception ex)
            {
                Debug.LogError($"[SensorBridge] Error parsing message: {ex.Message}");
            }
        }

        void ProcessAssetUpdates(TwinStreamMessage message)
        {
            foreach (var asset in message.assets)
            {
                if (string.IsNullOrEmpty(asset.asset_id))
                {
                    Debug.LogWarning("[SensorBridge] Received asset with null/empty ID");
                    continue;
                }
                
                // Update or add asset state
                LatestAssetStates[asset.asset_id] = asset;
                
                // Notify listeners
                OnAssetStateUpdated?.Invoke(asset.asset_id, asset);
            }
            
            // Log update summary
            Debug.Log($"[SensorBridge] Updated {message.assets.Count} assets at {message.timestamp}");
        }

        void OnWebSocketError(string error)
        {
            MainThreadDispatcher.Enqueue(() =>
            {
                Debug.LogError($"[SensorBridge] WebSocket error: {error}");
            });
        }

        void OnWebSocketClose(WebSocketCloseCode closeCode)
        {
            MainThreadDispatcher.Enqueue(async () =>
            {
                isConnected = false;
                Debug.LogWarning($"[SensorBridge] WebSocket closed: {closeCode}");
                OnConnectionStatusChanged?.Invoke(false);
                
                if (shouldReconnect)
                {
                    await ScheduleReconnect();
                }
            });
        }

        async Task ScheduleReconnect()
        {
            if (reconnectAttempts >= maxReconnectAttempts)
            {
                Debug.LogError($"[SensorBridge] Max reconnection attempts ({maxReconnectAttempts}) reached. Giving up.");
                return;
            }
            
            reconnectAttempts++;
            Debug.Log($"[SensorBridge] Reconnecting in {reconnectDelay}s (attempt {reconnectAttempts}/{maxReconnectAttempts})");
            
            await Task.Delay((int)(reconnectDelay * 1000));
            
            if (shouldReconnect)
            {
                await Connect();
            }
        }

        void Update()
        {
            // Dispatch WebSocket messages on main thread
            #if !UNITY_WEBGL || UNITY_EDITOR
            websocket?.DispatchMessageQueue();
            #endif
        }

        async void OnDestroy()
        {
            shouldReconnect = false;
            
            if (websocket != null && websocket.State == WebSocketState.Open)
            {
                Debug.Log("[SensorBridge] Closing WebSocket connection...");
                await websocket.Close();
            }
        }

        async void OnApplicationQuit()
        {
            shouldReconnect = false;
            
            if (websocket != null && websocket.State == WebSocketState.Open)
            {
                await websocket.Close();
            }
        }

        // Public API for manual reconnection
        public async void ManualReconnect()
        {
            if (websocket != null && websocket.State == WebSocketState.Open)
            {
                await websocket.Close();
            }
            
            reconnectAttempts = 0;
            await Connect();
        }

        // Get asset state by ID
        public static AssetState GetAssetState(string assetId)
        {
            if (LatestAssetStates.TryGetValue(assetId, out AssetState state))
            {
                return state;
            }
            return null;
        }

        // Check if asset exists in state dictionary
        public static bool HasAssetState(string assetId)
        {
            return LatestAssetStates.ContainsKey(assetId);
        }
    }
}

// Made with Bob
