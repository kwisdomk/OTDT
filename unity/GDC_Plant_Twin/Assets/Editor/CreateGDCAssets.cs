using UnityEngine;
using UnityEditor;

public class CreateGDCAssets : EditorWindow
{
    [MenuItem("GDC/Create All Assets")]
    static void CreateAssets()
    {
        // Define all 50 GDC assets
        string[] wellPumps = new string[20];
        for (int i = 1; i <= 20; i++)
            wellPumps[i-1] = $"GDC-WP-{i:D3}";

        string[] heatExchangers = new string[10];
        for (int i = 1; i <= 10; i++)
            heatExchangers[i-1] = $"GDC-HX-{i:D3}";

        string[] turbines = new string[10];
        for (int i = 1; i <= 10; i++)
            turbines[i-1] = $"GDC-TU-{i:D3}";

        string[] pipes = new string[10];
        for (int i = 1; i <= 10; i++)
            pipes[i-1] = $"GDC-PP-{i:D3}";

        var allAssets = new System.Collections.Generic.List<string>();
        allAssets.AddRange(wellPumps);
        allAssets.AddRange(heatExchangers);
        allAssets.AddRange(turbines);
        allAssets.AddRange(pipes);

        // Create parent container
        GameObject parent = new GameObject("GDC_Plant_Assets");

        // Create each asset as a cube with ColourController
        int row = 0;
        int col = 0;
        foreach (string assetId in allAssets)
        {
            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = assetId;
            go.transform.SetParent(parent.transform);
            
            // Position in grid layout (10 columns)
            go.transform.localPosition = new Vector3(col * 3f, 0, row * 3f);
            
            col++;
            if (col >= 10)
            {
                col = 0;
                row++;
            }
        }

        Debug.Log($"Created {allAssets.Count} GDC assets in grid layout");
        
        // Select the parent for easy viewing
        Selection.activeGameObject = parent;
    }
}

// Made with Bob
