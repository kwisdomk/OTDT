"""
Anomaly AI: Threshold-based detector for geothermal sensors.
Returns (status, anomaly_score) for each reading.

Supports both legacy keys and current simulator keys.
"""

# Canonical feature names for internal scoring
FEATURES = ["temperature", "pressure", "vibration", "flow"]

# Mapping: canonical feature -> accepted sensor keys (priority order)
KEY_MAP = {
    "temperature": ["bearing_temp_c", "temperature_c"],
    "pressure": ["steam_inlet_pressure_bar", "pressure_bar"],
    "vibration": ["bearing_vibration_mms", "vibration_mms"],
    "flow": ["steam_flow_kgs", "flow_rate_ls"],
}

# Thresholds tuned to simulator behavior
# Normal region is below NORMAL_MAX.
# Critical region is >= CRITICAL_MIN.
NORMAL_MAX = {
    "temperature": 90.0,
    "pressure": 75.0,
    "vibration": 5.0,
    "flow": 48.0,
}

CRITICAL_MIN = {
    "temperature": 105.0,
    "pressure": 85.0,
    "vibration": 7.1,
    "flow": 55.0,
}


def _first_float(sensors: dict, keys: list[str]):
    """Return first available numeric value for provided keys."""
    for key in keys:
        val = sensors.get(key)
        if val is None:
            continue
        try:
            return float(val)
        except (TypeError, ValueError):
            continue
    return None


class AnomalyDetector:
    def predict(self, sensors: dict) -> tuple[str, float]:
        """
        Returns (status, anomaly_score) where:
        - status: 'NORMAL' | 'WARNING' | 'CRITICAL' | 'UNKNOWN'
        - anomaly_score: 0.0 to 1.0
        """
        if not isinstance(sensors, dict):
            return "UNKNOWN", 0.0

        scores = []

        for feature in FEATURES:
            val = _first_float(sensors, KEY_MAP[feature])
            if val is None:
                continue

            nmax = NORMAL_MAX[feature]
            cmin = CRITICAL_MIN[feature]

            if val >= cmin:
                scores.append(1.0)
            elif val > nmax:
                # Warning band scaled to [0.6, 0.9)
                ratio = (val - nmax) / (cmin - nmax)
                scores.append(0.6 + (ratio * 0.3))
            else:
                # Normal band scaled to [0.0, 0.5]
                scores.append(max(0.0, (val / nmax) * 0.5))

        if not scores:
            return "UNKNOWN", 0.0

        score = max(scores)
        if score >= 0.9:
            return "CRITICAL", round(score, 4)
        if score >= 0.6:
            return "WARNING", round(score, 4)
        return "NORMAL", round(score, 4)


# Singleton instance
detector = AnomalyDetector()