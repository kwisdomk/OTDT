# OT Digital Twin — Sensor Simulator
# Publishes synthetic geothermal sensor data to Kafka

FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    kafka-python==2.0.2 \
    numpy==1.26.4 \
    python-dotenv==1.0.0

COPY . .

# Run in demo mode by default: injects anomaly at t=60s, clears at t=180s
CMD ["python", "kafka_publisher.py", "--demo"]
