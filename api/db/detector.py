"""

Anomaly AI: classifies live sensor reading as NORMAL / WARNING / CRITICAL.

Phase 1 (Days 1-6): threshold-based, no model needed.

Phase 2 (Days 7+): swap in trained CNN or LSTM inference.

"""

import numpy as np


FEATURES    = ['bearing_temp_c','bearing_vibration_mms','steam_inlet_temp_c',

               'steam_inlet_pressure_bar','turbine_rpm','steam_flow_kgs']

WARN_MAX    = [90.0,  5.0, 260.0, 75.0, 3060.0, 48.0]

CRIT_MAX    = [105.0, 7.1, 280.0, 85.0, 3100.0, 55.0]


class AnomalyDetector:

    def predict(self, sensors: dict) -> tuple[str, float]:

        """

        Returns (status, anomaly_score) where:

            status: 'NORMAL' | 'WARNING' | 'CRITICAL'

            anomaly_score: 0.0 to 1.0 (fraction of threshold breached)

        """

        scores = []

        for i, feat in enumerate(FEATURES):

            val = sensors.get(feat)

            if val is None: continue

            if val > CRIT_MAX[i]:

                scores.append(min(1.0, val / CRIT_MAX[i]))

            elif val > WARN_MAX[i]:

                scores.append(0.5 + 0.5 * (val - WARN_MAX[i]) / (CRIT_MAX[i] - WARN_MAX[i]))

            else:

                scores.append(val / CRIT_MAX[i] * 0.4)


        score = float(max(scores)) if scores else 0.0


        if score >= 0.95:  return 'CRITICAL', score

        if score >= 0.65:  return 'WARNING',  score

        return 'NORMAL', score


detector = AnomalyDetector()   # singleton
