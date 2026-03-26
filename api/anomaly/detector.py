"""
Anomaly AI: Threshold-based detector for geothermal sensors.
Returns (status, anomaly_score) for each reading.
"""

import numpy as np

# Features must match sensor_simulator output
FEATURES = ['temperature_c', 'pressure_bar', 'vibration_mms', 'flow_rate_ls']

# Normal operating ranges
NORMAL_MAX = {
    'temperature_c': 195.0,
    'pressure_bar': 28.0,
    'vibration_mms': 5.0,
    'flow_rate_ls': 90.0,
}

# Critical thresholds
CRITICAL_MIN = {
    'temperature_c': 210.0,
    'pressure_bar': 32.0,
    'vibration_mms': 7.5,
    'flow_rate_ls': 100.0,
}

class AnomalyDetector:
    def predict(self, sensors: dict) -> tuple:
        """
        Returns (status, anomaly_score) where:
        - status: 'NORMAL' | 'WARNING' | 'CRITICAL'
        - anomaly_score: 0.0 to 1.0
        """
        scores = []
        
        for name in FEATURES:
            val = sensors.get(name)
            if val is None:
                continue
            
            if val >= CRITICAL_MIN.get(name, float('inf')):
                scores.append(1.0)
            elif val > NORMAL_MAX.get(name, 0):
                ratio = (val - NORMAL_MAX[name]) / (CRITICAL_MIN[name] - NORMAL_MAX[name])
                scores.append(0.6 + (ratio * 0.3))
            else:
                # Normal zone: scale 0 to 0.5
                scores.append((val / NORMAL_MAX[name]) * 0.5)
        
        if not scores:
            return 'UNKNOWN', 0.0
        
        score = max(scores)
        if score >= 0.9:
            return 'CRITICAL', round(score, 4)
        if score >= 0.6:
            return 'WARNING', round(score, 4)
        return 'NORMAL', round(score, 4)

# Singleton instance
detector = AnomalyDetector()