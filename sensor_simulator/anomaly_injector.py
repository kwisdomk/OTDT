"""
anomaly_injector.py — OT Digital Twin Fault Injector
Injects pre-defined fault signatures into a running simulator via
a shared state file (for local demo) or directly via Kafka control topic.

Usage:
    python anomaly_injector.py --fault bearing_wear --asset WP-07
    python anomaly_injector.py --fault cavitation --asset WP-07 --delay 10
    python anomaly_injector.py --list-faults

Fault types:
    bearing_wear  — vibration spike (×4.5), ramps over 15 ticks
    cavitation    — pressure drop (×0.55), ramps over 10 ticks
    seal_leak     — flow collapse (×0.35), ramps over 20 ticks
    overheating   — temperature runaway (×1.18), ramps over 25 ticks

Author: Wisdom Kinoti / i3 Technologies
"""

import argparse
import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone

from config import ASSETS, FAULT_SIGNATURES, KAFKA_TOPIC_ANOMALIES, get_asset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("anomaly_injector")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
CONTROL_TOPIC = "simulator.control"

try:
    from aiokafka import AIOKafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False


def build_fault_event(asset_id: str, fault_name: str) -> dict:
    """Build a structured fault event payload."""
    asset = get_asset(asset_id)
    sig = FAULT_SIGNATURES[fault_name]
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "fault_injection",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "asset_id": asset.asset_id,
        "gdc_id": asset.gdc_id,
        "asset_type": asset.asset_type,
        "location": asset.location,
        "fault_name": fault_name,
        "fault_description": sig["description"],
        "affected_sensor": sig["sensor"],
        "severity": "CRITICAL" if sig["multiplier"] > 2 or sig["multiplier"] < 0.5 else "WARNING",
        "source": "anomaly_injector",
    }


async def publish_fault(asset_id: str, fault_name: str):
    """Publish fault event to Kafka anomaly.alerts + simulator.control topics."""
    event = build_fault_event(asset_id, fault_name)

    log.warning(
        f"INJECTING FAULT | Asset: {asset_id} | Fault: {fault_name} | "
        f"Sensor: {FAULT_SIGNATURES[fault_name]['sensor']} | "
        f"Severity: {event['severity']}"
    )
    print(json.dumps(event, indent=2))

    if not KAFKA_AVAILABLE:
        log.warning("Kafka not available — fault event printed to stdout only")
        return

    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
        )
        await producer.start()
        # Publish to anomaly alerts (picked up by API anomaly detector)
        await producer.send(KAFKA_TOPIC_ANOMALIES, event)
        # Publish to control topic (picked up by running simulator)
        await producer.send(CONTROL_TOPIC, {
            "command": "inject_fault",
            "asset_id": asset_id,
            "fault_name": fault_name,
        })
        await producer.flush()
        await producer.stop()
        log.info(f"Fault event published to Kafka topics: "
                 f"{KAFKA_TOPIC_ANOMALIES}, {CONTROL_TOPIC}")
    except Exception as e:
        log.error(f"Kafka publish failed: {e}")


def list_faults():
    print("\nAvailable fault signatures:\n")
    for name, sig in FAULT_SIGNATURES.items():
        print(f"  {name:<16} — {sig['description']}")
        print(f"  {'':>16}   Sensor: {sig['sensor']}, "
              f"Multiplier: {sig['multiplier']}×, "
              f"Ramp: {sig['ramp_steps']} ticks\n")


def parse_args():
    p = argparse.ArgumentParser(description="OTDT Anomaly Injector — GDC Kenya")
    p.add_argument("--asset", type=str, default="WP-07",
                   help="Target asset ID (default: WP-07)")
    p.add_argument("--fault", type=str, choices=list(FAULT_SIGNATURES.keys()),
                   help="Fault signature to inject")
    p.add_argument("--delay", type=int, default=0,
                   help="Seconds to wait before injecting (default: 0)")
    p.add_argument("--list-faults", action="store_true",
                   help="List all available fault signatures and exit")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.list_faults:
        list_faults()
        raise SystemExit(0)

    if not args.fault:
        print("Error: --fault is required. Use --list-faults to see options.")
        raise SystemExit(1)

    try:
        get_asset(args.asset)
    except KeyError as e:
        print(f"Error: {e}")
        raise SystemExit(1)

    if args.delay > 0:
        log.info(f"Waiting {args.delay}s before injecting '{args.fault}' on {args.asset}...")
        time.sleep(args.delay)

    asyncio.run(publish_fault(args.asset, args.fault))