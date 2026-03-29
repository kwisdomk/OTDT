using UnityEngine;

public class ColourController : MonoBehaviour
{
    public string assetId;
    private Renderer rend;

    void Awake()
    {
        rend = GetComponent<Renderer>();
    }

    void OnEnable()
    {
        SensorBridge.OnAssetStateUpdated += HandleAssetStateUpdate;
    }

    void OnDisable()
    {
        SensorBridge.OnAssetStateUpdated -= HandleAssetStateUpdate;
    }

    void HandleAssetStateUpdate(string updatedId, AssetState state)
    {
        if (updatedId != assetId)
            return;

        string status = state.status.ToUpper();

        if (status == "CAUTION" || status == "WARNING")
        {
            rend.material.color = new Color(1f, 0.65f, 0f); // Orange
        }
        else if (status == "ALARM" || status == "CRITICAL")
        {
            rend.material.color = Color.red;
        }
        else // NORMAL
        {
            rend.material.color = Color.green;
        }
    }
}

// Made with Bob
