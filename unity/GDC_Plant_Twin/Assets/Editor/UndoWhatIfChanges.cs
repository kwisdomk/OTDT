using UnityEngine;
using UnityEngine.UI;
using UnityEditor;
using UnityEditor.SceneManagement;

public class UndoWhatIfChanges : EditorWindow
{
    [MenuItem("GDC/Undo WhatIf Changes")]
    static void UndoChanges()
    {
        // Find Canvas in scene
        Canvas canvas = GameObject.FindObjectOfType<Canvas>();
        if (canvas == null)
        {
            Debug.LogError("Canvas not found in scene!");
            return;
        }

        // Find WhatIfPanel
        Transform whatIfPanel = canvas.transform.Find("WhatIfPanel");
        if (whatIfPanel == null)
        {
            Debug.LogWarning("WhatIfPanel not found - changes may have already been undone");
            return;
        }

        // Move children back to Canvas before deleting panel
        string[] elementNames = { "WhatIfSlider", "DeferralDaysText", "FailureProbabilityText", "ExpectedCostText" };
        
        foreach (string elementName in elementNames)
        {
            Transform element = whatIfPanel.Find(elementName);
            if (element != null)
            {
                element.SetParent(canvas.transform, true); // Keep world position
                Debug.Log($"Moved {elementName} back to Canvas");
            }
        }

        // Delete the WhatIfPanel
        GameObject.DestroyImmediate(whatIfPanel.gameObject);
        Debug.Log("Deleted WhatIfPanel");

        // Mark scene as dirty and save
        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        EditorSceneManager.SaveOpenScenes();
        
        Debug.Log("✅ WhatIf changes undone successfully! UI elements are back under Canvas with their previous settings.");
    }
}

// Made with Bob
