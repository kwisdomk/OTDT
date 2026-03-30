using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.Collections;
using Newtonsoft.Json;

public class WhatIfSlider : MonoBehaviour
{
    [Header("UI Components")]
    public Slider deferralSlider;
    public Text deferralDaysText;
    public Text failureProbabilityText;
    public Text expectedCostText;
    
    [Header("Configuration")]
    public string apiUrl = "http://localhost:8000/api/monte-carlo/whatif";
    public string targetAssetId = "GDC-WP-007";
    
    private const float FAILURE_COST_USD = 180000f;
    private const float INSPECTION_COST_USD = 8000f;

    void Start()
    {
        if (deferralSlider != null)
        {
            deferralSlider.minValue = 0;
            deferralSlider.maxValue = 180;
            deferralSlider.value = 0;
            deferralSlider.onValueChanged.AddListener(OnSliderValueChanged);
        }
        
        // Initial query at 0 days
        StartCoroutine(QueryWhatIf(0));
    }

    void OnSliderValueChanged(float value)
    {
        int days = Mathf.RoundToInt(value);
        
        // Update deferral days text immediately
        if (deferralDaysText != null)
        {
            deferralDaysText.text = $"Deferral: {days} days";
        }
        
        // Query API with rounded value
        StartCoroutine(QueryWhatIf(days));
    }

    IEnumerator QueryWhatIf(int deferralDays)
    {
        string jsonBody = JsonConvert.SerializeObject(new
        {
            asset_id = targetAssetId,
            deferral_days = deferralDays
        });

        using (UnityWebRequest request = new UnityWebRequest(apiUrl, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonBody);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string responseText = request.downloadHandler.text;
                var response = JsonConvert.DeserializeObject<WhatIfResponse>(responseText);
                
                // Update UI with response data
                UpdateUI(response, deferralDays);
            }
            else
            {
                Debug.LogError($"What-If API Error: {request.error}");
                if (failureProbabilityText != null)
                {
                    failureProbabilityText.text = "API Error";
                }
                if (expectedCostText != null)
                {
                    expectedCostText.text = "API Error";
                }
            }
        }
    }

    void UpdateUI(WhatIfResponse response, int deferralDays)
    {
        float probabilityPercent = response.failure_probability * 100f;
        
        // Update failure probability text
        if (failureProbabilityText != null)
        {
            failureProbabilityText.text = $"Failure Probability: {probabilityPercent:F1}%";
        }
        
        // Update expected cost text
        if (expectedCostText != null)
        {
            float expectedCost = response.failure_probability * FAILURE_COST_USD;
            expectedCostText.text = $"Expected Cost: ${expectedCost:N0}";
        }
        
        Debug.Log($"What-If: {deferralDays} days → {probabilityPercent:F1}% failure probability");
    }

    [System.Serializable]
    public class WhatIfResponse
    {
        public string asset_id;
        public int deferral_days;
        public float failure_probability;
        public string recommendation;
    }


// Made with Bob


}
