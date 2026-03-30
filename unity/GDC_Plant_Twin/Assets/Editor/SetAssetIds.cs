using UnityEngine;
using UnityEditor;

public class SetAssetIds : EditorWindow
{
    [MenuItem("GDC/Set Asset IDs")]
    static void SetIds()
    {
        GameObject parent = GameObject.Find("GDC_Plant_Assets");
        if (parent == null) { Debug.LogError("GDC_Plant_Assets not found"); return; }
        
        int count = 0;
        foreach (Transform child in parent.transform)
        {
            ColourController cc = child.gameObject.GetComponent<ColourController>();
            if (cc != null)
            {
                cc.assetId = child.gameObject.name;
                EditorUtility.SetDirty(cc);
                count++;
            }
        }
        Debug.Log("Set assetId on " + count + " ColourControllers");
    }
}
