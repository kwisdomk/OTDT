using UnityEngine;

public class AssetIdInitializer : MonoBehaviour
{
    void Start()
    {
        ColourController cc = GetComponent<ColourController>();
        if (cc != null && string.IsNullOrEmpty(cc.assetId))
        {
            cc.assetId = gameObject.name;
            Debug.Log("Set assetId: " + gameObject.name);
        }
    }



}
