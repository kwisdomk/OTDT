using UnityEngine;
using UnityEngine.UI;
using UnityEditor;
using UnityEditor.SceneManagement;

public class FixWhatIfLayout : EditorWindow
{
    [MenuItem("GDC/Fix WhatIf Layout")]
    static void FixLayout()
    {
        // Find Canvas in scene
        Canvas canvas = GameObject.FindObjectOfType<Canvas>();
        if (canvas == null)
        {
            Debug.LogError("Canvas not found in scene!");
            return;
        }

        // Create WhatIfPanel if it doesn't exist
        Transform existingPanel = canvas.transform.Find("WhatIfPanel");
        GameObject whatIfPanel;
        
        if (existingPanel != null)
        {
            whatIfPanel = existingPanel.gameObject;
            Debug.Log("WhatIfPanel already exists, updating it...");
        }
        else
        {
            whatIfPanel = new GameObject("WhatIfPanel");
            whatIfPanel.transform.SetParent(canvas.transform, false);
            whatIfPanel.AddComponent<Image>();
            Debug.Log("Created new WhatIfPanel");
        }

        // Setup WhatIfPanel RectTransform - middle-right anchor
        RectTransform panelRect = whatIfPanel.GetComponent<RectTransform>();
        if (panelRect == null)
        {
            panelRect = whatIfPanel.AddComponent<RectTransform>();
        }
        
        panelRect.anchorMin = new Vector2(1, 0.5f);
        panelRect.anchorMax = new Vector2(1, 0.5f);
        panelRect.pivot = new Vector2(1, 0.5f);
        panelRect.anchoredPosition = new Vector2(-10, 0);
        panelRect.sizeDelta = new Vector2(280, 130);

        // Setup panel background color
        Image panelImage = whatIfPanel.GetComponent<Image>();
        if (panelImage != null)
        {
            panelImage.color = new Color(0.1f, 0.1f, 0.1f, 0.8f);
        }

        // Find and reparent UI elements
        string[] elementNames = { "WhatIfSlider", "DeferralDaysText", "FailureProbabilityText", "ExpectedCostText" };
        
        foreach (string elementName in elementNames)
        {
            Transform element = FindInCanvas(canvas.transform, elementName);
            if (element != null)
            {
                element.SetParent(whatIfPanel.transform, false);
                Debug.Log($"Reparented {elementName} under WhatIfPanel");
            }
            else
            {
                Debug.LogWarning($"{elementName} not found in Canvas!");
            }
        }

        // Configure DeferralDaysText - top
        Transform deferralText = whatIfPanel.transform.Find("DeferralDaysText");
        if (deferralText != null)
        {
            RectTransform textRect = deferralText.GetComponent<RectTransform>();
            textRect.anchorMin = new Vector2(0.5f, 1);
            textRect.anchorMax = new Vector2(0.5f, 1);
            textRect.pivot = new Vector2(0.5f, 1);
            textRect.anchoredPosition = new Vector2(0, -10);
            textRect.sizeDelta = new Vector2(260, 25);
            
            Text text = deferralText.GetComponent<Text>();
            if (text != null) text.fontSize = 14;
            Debug.Log("Configured DeferralDaysText");
        }

        // Configure FailureProbabilityText
        Transform failureText = whatIfPanel.transform.Find("FailureProbabilityText");
        if (failureText != null)
        {
            RectTransform textRect = failureText.GetComponent<RectTransform>();
            textRect.anchorMin = new Vector2(0.5f, 1);
            textRect.anchorMax = new Vector2(0.5f, 1);
            textRect.pivot = new Vector2(0.5f, 1);
            textRect.anchoredPosition = new Vector2(0, -40);
            textRect.sizeDelta = new Vector2(260, 25);
            
            Text text = failureText.GetComponent<Text>();
            if (text != null) text.fontSize = 14;
            Debug.Log("Configured FailureProbabilityText");
        }

        // Configure ExpectedCostText
        Transform costText = whatIfPanel.transform.Find("ExpectedCostText");
        if (costText != null)
        {
            RectTransform textRect = costText.GetComponent<RectTransform>();
            textRect.anchorMin = new Vector2(0.5f, 1);
            textRect.anchorMax = new Vector2(0.5f, 1);
            textRect.pivot = new Vector2(0.5f, 1);
            textRect.anchoredPosition = new Vector2(0, -70);
            textRect.sizeDelta = new Vector2(260, 25);
            
            Text text = costText.GetComponent<Text>();
            if (text != null) text.fontSize = 12;
            Debug.Log("Configured ExpectedCostText");
        }

        // Configure WhatIfSlider - bottom
        Transform sliderTransform = whatIfPanel.transform.Find("WhatIfSlider");
        if (sliderTransform != null)
        {
            RectTransform sliderRect = sliderTransform.GetComponent<RectTransform>();
            sliderRect.anchorMin = new Vector2(0.5f, 1);
            sliderRect.anchorMax = new Vector2(0.5f, 1);
            sliderRect.pivot = new Vector2(0.5f, 1);
            sliderRect.anchoredPosition = new Vector2(0, -100);
            sliderRect.sizeDelta = new Vector2(260, 25);
            Debug.Log("Configured WhatIfSlider");
        }

        // Mark scene as dirty and save
        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        EditorSceneManager.SaveOpenScenes();
        
        Debug.Log("✅ WhatIf layout fixed successfully!");
    }

    // Helper method to find GameObject in Canvas hierarchy
    static Transform FindInCanvas(Transform parent, string name)
    {
        // Check direct children first
        Transform found = parent.Find(name);
        if (found != null) return found;

        // Search recursively
        foreach (Transform child in parent)
        {
            found = FindInCanvas(child, name);
            if (found != null) return found;
        }

        return null;
    }
}

// Made with Bob
