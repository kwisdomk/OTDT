import numpy as np
from datetime import datetime, timezone

from config import ASSET_ID, ASSET_TYPE


class GeothermalSimulator:
    """
    Simulates GDC Kenya geothermal turbine sensor telemetry.
    Models slow bearing degradation (drift) and supports on-command anomaly injection.
    """
    def __init__(self):
        self.step = 0
        self.bearing_drift = 0.0   # mm/s accumulated wear
        self.anomaly_active = False

    def get_reading(self) -> dict:
        self.step += 1
        self.bearing_drift += 0.002   # 0.002 mm/s per second = ~0.17/day degradation

        if self.anomaly_active:
            vib = np.random.normal(9.5,  0.3)    # spike into critical zone
            tmp = np.random.normal(108,  2.0)
        else:
            vib = np.random.normal(4.2 + self.bearing_drift, 0.15)
            tmp = np.random.normal(83  + self.bearing_drift * 2, 1.0)

        return {
            'asset_id':   ASSET_ID,
            'asset_type': ASSET_TYPE,
            'timestamp':  datetime.now(timezone.utc).isoformat(),
            'sensors': {
                'bearing_temp_c':             round(float(tmp), 2),
                'bearing_vibration_mms':      round(float(vib), 3),
                'steam_inlet_temp_c':         round(float(np.random.normal(245, 3.0)), 2),
                'steam_inlet_pressure_bar':   round(float(np.random.normal(68,  1.5)), 2),
                'turbine_rpm':                round(float(np.random.normal(3000, 8)),  1),
                'steam_flow_kgs':             round(float(np.random.normal(42,  1.2)), 2),
            },
            'is_anomaly_injected': self.anomaly_active
        }

    def inject_anomaly(self):  self.anomaly_active = True
    def clear_anomaly(self):   self.anomaly_active = False; self.bearing_drift = 0.0

# Add this at the end of simulator.py

if __name__ == "__main__":
    import sys
    import time
    import json
    from kafka import KafkaProducer
    
    # Create producer
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print("[SIM] Publishing to Kafka topic sensor.telemetry every 1s")
    
    sim = GeothermalSimulator()
    DEMO_MODE = '--demo' in sys.argv
    demo_timer = 0
    
    try:
        while True:
            if DEMO_MODE:
                demo_timer += 1
                if 60 <= demo_timer < 180 and not sim.anomaly_active:
                    sim.inject_anomaly()
                    print('[SIM] ANOMALY INJECTED at t=60s')
                elif demo_timer >= 180 and sim.anomaly_active:
                    sim.clear_anomaly()
                    print('[SIM] Anomaly cleared at t=180s')
            
            payload = sim.get_reading()
            producer.send('sensor.telemetry', payload)
            vib = payload['sensors']['bearing_vibration_mms']
            print(f'[SIM] Sent: {vib:.3f}mm vib')
            time.sleep(1)
            
    except KeyboardInterrupt:
        print('[SIM] Stopped')
        producer.close()
