import numpy as np

# Features must match Philip's simulator output
FEATURES    = ['bearing_temp_c','bearing_vibration_mms','steam_inlet_temp_c',
               'steam_inlet_pressure_bar','turbine_rpm','steam_flow_kgs']
WARN_MAX    = [90.0,  5.0, 260.0, 75.0, 3060.0, 48.0]
CRIT_MAX    = [105.0, 7.1, 280.0, 85.0, 3100.0, 55.0]

class AnomalyDetector:
    def predict(self, sensors: dict) -> tuple:
        """Returns (status, anomaly_score) where score is 0.0 to 1.0."""
        scores = []
        for i, feat in enumerate(FEATURES):
            val = sensors.get(feat)
            if val is None:
                continue
            
            if val >= CRIT_MAX[i]:
                scores.append(1.0)
            elif val > WARN_MAX[i]:
                # Linear scaling for the WARNING zone
                ratio = (val - WARN_MAX[i]) / (CRIT_MAX[i] - WARN_MAX[i])
                scores.append(0.6 + (ratio * 0.3))
            else:
                # Normal zone scaling
                scores.append((val / WARN_MAX[i]) * 0.5)

        score = max(scores) if scores else 0.0
        if score >= 0.9:
            status = 'CRITICAL'
        elif score >= 0.6:
            status = 'WARNING'
        else:
            status = 'NORMAL'
        return status, round(float(score), 4)

detector = AnomalyDetector()