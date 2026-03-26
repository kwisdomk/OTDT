import numpy as np

# Features must match Philip's simulator output
FEATURES = ['temperature_c', 'pressure_bar', 'vibration_mms', 'flow_rate_ls']
WARN_MAX = [195.0, 28.0, 5.0, 90.0]
CRIT_MAX = [210.0, 32.0, 7.5, 100.0]

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