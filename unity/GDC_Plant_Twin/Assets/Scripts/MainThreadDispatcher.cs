// unity/GDC_Plant_Twin/Assets/Scripts/MainThreadDispatcher.cs
// Handles execution of callbacks on Unity's main thread
// Required for WebSocket callbacks which run on background threads
// Build Guide v1.0 - Step 3: Unity XR 3D Model Construction (Lines 207-238)

using System;
using System.Collections.Generic;
using UnityEngine;

namespace GDCPlantTwin
{
    /// <summary>
    /// Singleton that dispatches actions to Unity's main thread
    /// WebSocket callbacks run on background threads and cannot directly modify Unity objects
    /// </summary>
    public class MainThreadDispatcher : MonoBehaviour
    {
        private static MainThreadDispatcher _instance;
        private static readonly Queue<Action> _executionQueue = new Queue<Action>();
        private static readonly object _lock = new object();

        public static MainThreadDispatcher Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("MainThreadDispatcher");
                    _instance = go.AddComponent<MainThreadDispatcher>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
            }
        }

        void Update()
        {
            // Execute all queued actions on the main thread
            lock (_lock)
            {
                while (_executionQueue.Count > 0)
                {
                    try
                    {
                        _executionQueue.Dequeue().Invoke();
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"[MainThreadDispatcher] Error executing queued action: {ex.Message}");
                    }
                }
            }
        }

        /// <summary>
        /// Enqueue an action to be executed on the main thread
        /// </summary>
        public static void Enqueue(Action action)
        {
            if (action == null)
            {
                Debug.LogWarning("[MainThreadDispatcher] Attempted to enqueue null action");
                return;
            }

            lock (_lock)
            {
                _executionQueue.Enqueue(action);
            }
        }

        /// <summary>
        /// Check if we're currently on the main thread
        /// </summary>
        public static bool IsMainThread()
        {
            return System.Threading.Thread.CurrentThread.ManagedThreadId == 1;
        }
    }
}

// Made with Bob
