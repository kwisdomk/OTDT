from kafka import KafkaProducer
import json
from datetime import datetime, timezone

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

data = {
    "asset_id": "WP-07",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "sensors": {
        "temperature_c": 185.5,
        "pressure_bar": 25.2,
        "vibration_mms": 4.3,
        "flow_rate_ls": 86.1
    }
}

producer.send('sensor.telemetry', data)
producer.flush()
print("✅ Data sent to Kafka")
producer.close()
