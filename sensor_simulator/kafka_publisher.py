import json, time, sys, os
import numpy as np
from datetime import datetime, timezone
from kafka import KafkaProducer
from config import INTERVAL, ASSET_ID, ASSET_TYPE

# Read from env so Docker Compose can inject kafka:9092 (container network)
# Fallback to localhost:29092 for direct host-machine use
BROKER = os.getenv('KAFKA_BROKER', 'localhost:29092')
TOPIC  = os.getenv('KAFKA_TOPIC', 'sensor.telemetry')

producer = KafkaProducer(
    bootstrap_servers=[BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5,
    retry_backoff_ms=500,
)

print(f'[KAFKA] Publishing to {BROKER} topic {TOPIC} every {INTERVAL}s | --demo for timed anomaly')

class GeothermalSimulator:
    def __init__(self):
        self.step = 0
        self.bearing_drift = 0.0
        self.anomaly_active = False

    def get_reading(self):
        self.step += 1
        self.bearing_drift += 0.002

        if self.anomaly_active:
            vib = np.random.normal(9.5, 0.3)
            tmp = np.random.normal(108, 2.0)
        else:
            vib = np.random.normal(4.2 + self.bearing_drift, 0.15)
            tmp = np.random.normal(83 + self.bearing_drift * 2, 1.0)

        reading = {
            'asset_id': ASSET_ID,
            'asset_type': ASSET_TYPE,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sensors': {
                'bearing_temp_c': round(float(tmp), 2),
                'bearing_vibration_mms': round(float(vib), 3),
                'steam_inlet_temp_c': round(float(np.random.normal(245, 3.0)), 2),
                'steam_inlet_pressure_bar': round(float(np.random.normal(68, 1.5)), 2),
                'turbine_rpm': round(float(np.random.normal(3000, 8)), 1),
                'steam_flow_kgs': round(float(np.random.normal(42, 1.2)), 2),
            },
            'is_anomaly_injected': self.anomaly_active
        }
        return reading

    def inject_anomaly(self): self.anomaly_active = True
    def clear_anomaly(self): self.anomaly_active = False; self.bearing_drift = 0.0

sim = GeothermalSimulator()

DEMO_MODE = '--demo' in sys.argv
demo_timer = 0

try:
    while True:
        if DEMO_MODE:
            demo_timer += INTERVAL
            if 60 <= demo_timer < 180 and not sim.anomaly_active:
                sim.inject_anomaly()
                print('[SIM] ANOMALY INJECTED at t=60s')
            elif demo_timer >= 180 and sim.anomaly_active:
                sim.clear_anomaly()
                print('[SIM] Anomaly cleared at t=180s')

        payload = sim.get_reading()
        future = producer.send(TOPIC, payload)
        future.get(timeout=5)
        vib = payload['sensors']['bearing_vibration_mms']
        print(f'[KAFKA] Sent: {vib:.3f}mm vib')
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print('[KAFKA] Stopped')
    producer.close()

