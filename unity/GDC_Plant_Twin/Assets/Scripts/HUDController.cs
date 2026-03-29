using UnityEngine;
using TMPro;
using UnityEngine.Networking;
using System.Collections;
using UnityEngine.UI;

public class HUDController : MonoBehaviour
{
    public TMP_Text assetIdText;
    public TMP_Text statusText;
    public TMP_Text temperatureText;
    public TMP_Text pressureText;
    public TMP_Text vibrationText;
    public TMP_Text flowRateText;
    public TMP_Text rotationText;
    public TMP_Text healthScoreText;
    public TMP_Text failureProbabilityText;
    public TMP_Text recommendedActionText;
    public TMP_Text disclaimerText;
    public GameObject hudPanel;

    void Start()
    {
        if (disclaimerText != null)
        {
            disclaimerText.text = "SYNTHETIC DATA: Computer-generated";
        }
        
        if (hudPanel != null)
        {
            hudPanel.SetActive(false);
        }
    }

    public void SelectAsset(string assetId)
    {
        if (hudPanel != null)
        {
            hudPanel.SetActive(true);
        }
        
        StartCoroutine(FetchSensorData(assetId));
    }

    public void DeselectAsset()
    {
        if (hudPanel != null)
        {
            hudPanel.SetActive(false);
        }
    }

    IEnumerator FetchSensorData(string assetId)
    {
        string url = $"http://localhost:8000/api/twins/{assetId}/sensors/latest";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string json = request.downloadHandler.text;
                
                // Parse JSON response
                string status = ExtractValue(json, "status");
                string temperature_c = ExtractValue(json, "temperature_c");
                string pressure_bar = ExtractValue(json, "pressure_bar");
                string vibration_mm_s = ExtractValue(json, "vibration_mm_s");
                string flow_rate_kg_s = ExtractValue(json, "flow_rate_kg_s");
                string rotation_rpm = ExtractValue(json, "rotation_rpm");
                string health_score = ExtractValue(json, "health_score");

                // Update text fields
                if (assetIdText != null)
                    assetIdText.text = $"Asset: {assetId}";
                
                if (statusText != null)
                    statusText.text = $"Status: {status}";
                
                if (temperatureText != null)
                    temperatureText.text = $"Temperature: {temperature_c}°C";
                
                if (pressureText != null)
                    pressureText.text = $"Pressure: {pressure_bar} bar";
                
                if (vibrationText != null)
                    vibrationText.text = $"Vibration: {vibration_mm_s} mm/s";
                
                if (flowRateText != null)
                    flowRateText.text = $"Flow Rate: {flow_rate_kg_s} kg/s";
                
                if (rotationText != null)
                    rotationText.text = $"Rotation: {rotation_rpm.Trim().TrimEnd('}')} RPM";
                
                if (healthScoreText != null)
                    healthScoreText.text = $"Health Score: {health_score}%";

                // Special handling for GDC-WP-007
                if (failureProbabilityText != null)
                {
                    if (assetId == "GDC-WP-007")
                    {
                        failureProbabilityText.text = "34% — Failure within 30 days";
                    }
                    else
                    {
                        failureProbabilityText.text = "8% — Normal operation";
                    }
                }

                // Recommended action based on status
                if (recommendedActionText != null)
                {
                    string statusUpper = status.ToUpper();
                    if (statusUpper == "CAUTION" || statusUpper == "WARNING")
                    {
                        recommendedActionText.text = "Schedule Maintenance";
                    }
                    else if (statusUpper == "ALARM" || statusUpper == "CRITICAL")
                    {
                        recommendedActionText.text = "URGENT: Immediate Action Required";
                    }
                    else
                    {
                        recommendedActionText.text = "Monitor";
                    }
                }
            }
            else
            {
                Debug.LogError($"Failed to fetch data for {assetId}: {request.error}");
                
                if (assetIdText != null)
                    assetIdText.text = $"Asset: {assetId}";
                
                if (statusText != null)
                    statusText.text = "Status: ERROR - Cannot connect to API";
            }
        }
    }

    string ExtractValue(string json, string key)
    {
        string searchKey = "\"" + key + "\"";
        int startIndex = json.IndexOf(searchKey);
        if (startIndex == -1) return "N/A";

        startIndex = json.IndexOf(":", startIndex) + 1;
        int endIndex = json.IndexOf(",", startIndex);
        if (endIndex == -1) endIndex = json.IndexOf("}", startIndex);

        string value = json.Substring(startIndex, endIndex - startIndex).Trim();
        value = value.Replace("\"", "").Replace(",", "");
        
        return value;
    }
}

// Made with Bob
