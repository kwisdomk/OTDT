"""
watson_iot_publisher.py — Watson IoT Platform MQTT Publisher
Bridges local Kafka telemetry stream → IBM Watson IoT Platform via MQTT/TLS.

Consumes: Kafka topic sensor.telemetry
Publishes: iot-2/evt/telemetry/fmt/json (Watson IoT format)

Watson IoT MQTT topic format:
    iot-2/evt/{event_type}/fmt/{format}

Device credentials from .env:
    WATSON_IOT_ORG_ID      — 6-char org ID from Watson IoT dashboard
    WATSON_IOT_DEVICE_TYPE — e.g. "GDC-Sensor-Gateway"
    WATSON_IOT_DEVICE_ID   — e.g. "OTDT-Gateway-01"
    WATSON_IOT_AUTH_TOKEN  — device auth token

Author: Wisdom Kinoti / i3 Technologies
"""

import asyncio
import json
import logging
import os
import ssl
import time
from typing import Optional

log = logging.getLogger("watson_iot_publisher")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

# ── Watson IoT credentials ────────────────────────────────────────────────────
ORG_ID      = os.getenv("WATSON_IOT_ORG_ID", "")
DEVICE_TYPE = os.getenv("WATSON_IOT_DEVICE_TYPE", "GDC-Sensor-Gateway")
DEVICE_ID   = os.getenv("WATSON_IOT_DEVICE_ID", "OTDT-Gateway-01")
AUTH_TOKEN  = os.getenv("WATSON_IOT_AUTH_TOKEN", "")

WATSON_BROKER = f"{ORG_ID}.messaging.internetofthings.ibmcloud.com"
WATSON_PORT   = 8883  # TLS
CLIENT_ID     = f"d:{ORG_ID}:{DEVICE_TYPE}:{DEVICE_ID}"
MQTT_TOPIC    = "iot-2/evt/telemetry/fmt/json"

# ── Kafka config ──────────────────────────────────────────────────────────────
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_IN  = "sensor.telemetry"
KAFKA_GROUP     = "watson-iot-bridge"

# ── Optional imports ──────────────────────────────────────────────────────────
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    log.warning("paho-mqtt not installed — run: pip install paho-mqtt")

try:
    from aiokafka import AIOKafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    log.warning("aiokafka not installed — Kafka consumer unavailable")


# ── MQTT client ───────────────────────────────────────────────────────────────

class WatsonIoTClient:
    """Manages MQTT connection to Watson IoT Platform with auto-reconnect."""

    def __init__(self):
        if not MQTT_AVAILABLE:
            raise RuntimeError("paho-mqtt required: pip install paho-mqtt")
        if not ORG_ID or not AUTH_TOKEN:
            raise RuntimeError(
                "Watson IoT credentials missing — set WATSON_IOT_ORG_ID and "
                "WATSON_IOT_AUTH_TOKEN in .env"
            )
        self._client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
        self._client.username_pw_set("use-token-auth", AUTH_TOKEN)
        self._client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
        self._client.on_connect    = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish    = self._on_publish
        self._connected = False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            log.info(f"Watson IoT connected → {WATSON_BROKER}:{WATSON_PORT}")
        else:
            log.error(f"Watson IoT connection failed, rc={rc}")

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        if rc != 0:
            log.warning(f"Watson IoT unexpected disconnect (rc={rc}) — will retry")

    def _on_publish(self, client, userdata, mid):
        log.debug(f"Watson IoT published mid={mid}")

    def connect(self):
        log.info(f"Connecting to Watson IoT: {WATSON_BROKER}:{WATSON_PORT}")
        self._client.connect(WATSON_BROKER, WATSON_PORT, keepalive=60)
        self._client.loop_start()
        # Wait up to 10s for connection
        for _ in range(20):
            if self._connected:
                return
            time.sleep(0.5)
        raise TimeoutError("Watson IoT connection timed out after 10s")

    def publish(self, payload: dict) -> bool:
        """Publish a telemetry payload. Returns True on success."""
        if not self._connected:
            log.warning("Watson IoT not connected — skipping publish")
            return False
        result = self._client.publish(
            MQTT_TOPIC,
            json.dumps(payload).encode("utf-8"),
            qos=1,
        )
        return result.rc == mqtt.MQTT_ERR_SUCCESS

    def disconnect(self):
        self._client.loop_stop()
        self._client.disconnect()
        log.info("Watson IoT disconnected")


# ── Bridge loop ───────────────────────────────────────────────────────────────

async def run_bridge():
    """Consume Kafka telemetry and forward to Watson IoT Platform."""
    if not KAFKA_AVAILABLE:
        raise RuntimeError("aiokafka required: pip install aiokafka")

    watson = WatsonIoTClient()
    watson.connect()

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC_IN,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=KAFKA_GROUP,
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        auto_offset_reset="latest",
    )
    await consumer.start()
    log.info(f"Kafka consumer started — topic: {KAFKA_TOPIC_IN}")

    published = 0
    failed = 0

    try:
        async for msg in consumer:
            payload = msg.value
            ok = watson.publish(payload)
            if ok:
                published += 1
                if published % 100 == 0:
                    log.info(f"Published {published} messages to Watson IoT "
                             f"(failed: {failed})")
            else:
                failed += 1

    except asyncio.CancelledError:
        log.info("Bridge cancelled")
    finally:
        await consumer.stop()
        watson.disconnect()
        log.info(f"Bridge stopped — published: {published}, failed: {failed}")


# ── Smoke test (no Kafka) ──────────────────────────────────────────────────────

async def smoke_test():
    """Send a single test message to Watson IoT without Kafka."""
    watson = WatsonIoTClient()
    watson.connect()

    test_payload = {
        "asset_id": "WP-07",
        "gdc_id": "GDC-WP-007",
        "sensors": {
            "temperature_c": 178.4,
            "pressure_bar": 24.1,
            "vibration_mms": 3.2,
            "flow_rate_ls": 82.0,
        },
        "anomaly_score": 0.12,
        "status": "NORMAL",
        "source": "smoke_test",
    }

    ok = watson.publish(test_payload)
    log.info(f"Smoke test publish: {'SUCCESS' if ok else 'FAILED'}")
    await asyncio.sleep(1)  # Let MQTT ACK arrive
    watson.disconnect()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Watson IoT MQTT Bridge")
    p.add_argument("--smoke-test", action="store_true",
                   help="Send single test message and exit")
    args = p.parse_args()

    try:
        if args.smoke_test:
            asyncio.run(smoke_test())
        else:
            asyncio.run(run_bridge())
    except KeyboardInterrupt:
        log.info("Stopped by user")
    except RuntimeError as e:
        log.error(str(e))
        raise SystemExit(1)