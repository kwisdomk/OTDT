"""OTDT Sensor Simulator.

Publishes synthetic sensor telemetry for GDC-WP-007 to Kafka topic 'sensor.telemetry'.
- Normal mode: realistic pump values
- Anomaly injection: t=60-180s (high vib/temp)
Run: python simulator.py
Stop: Ctrl+C

Dependencies: kafka-python, numpy
"""
import numpy as np
import time
import json
from datetime import datetime, timezone
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print('[SIM] Publishing to Kafka topic sensor.telemetry every 1s')

asset_id = "GDC-WP-007"
step = 0
anomaly_active = False
demo_mode = True
demo_timer = 0

try:
    while True:
        step += 1
        demo_timer += 1
        
        if demo_mode and 60 <= demo_timer < 180 and not anomaly_active:
            anomaly_active = True
            print('[SIM] ANOMALY INJECTED at t=60s')
        elif demo_timer >= 180 and anomaly_active:
            anomaly_active = False
            print('[SIM] Anomaly cleared at t=180s')
        
        if anomaly_active:
            vib = np.random.normal(9.5, 0.3)
            temp = np.random.normal(108, 2.0)
        else:
            vib = np.random.normal(4.2, 0.15)
            temp = np.random.normal(83, 1.0)
        
        data = {
            "asset_id": asset_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sensors": {
                "temperature_c": round(temp, 2),
                "pressure_bar": round(np.random.normal(25, 1.5), 2),
                "vibration_mms": round(vib, 3),
                "flow_rate_ls": round(np.random.normal(85, 3), 2)
            }
        }
        
        producer.send('sensor.telemetry', data)
        print(f'[SIM] Sent: {vib:.3f}mm vib')
        time.sleep(1)
        
except KeyboardInterrupt:
    print('[SIM] Stopped')
    producer.close()
