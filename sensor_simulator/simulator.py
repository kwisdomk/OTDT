"""
simulator.py — OT Digital Twin Sensor Simulator
Generates realistic geothermal telemetry for all 50 GDC Kenya assets.

Usage:
    python simulator.py                          # all assets, normal mode
    python simulator.py --asset WP-07            # single asset
    python simulator.py --demo --asset WP-07     # injects bearing_wear after 30s
    python simulator.py --no-kafka               # stdout only, no Kafka

Publishes JSON to:
    - stdout (always)
    - Kafka topic: sensor.telemetry (unless --no-kafka)

Author: Wisdom Kinoti / i3 Technologies
"""

import argparse
import asyncio
import json
import logging
import os
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from config import (
    ASSETS, DEMO_ASSET_ID, FAULT_SIGNATURES, KAFKA_TOPIC_TELEMETRY,
    TELEMETRY_INTERVAL_S, AssetConfig, SensorRange, get_asset,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("simulator")

# ── Kafka (optional — graceful degradation if not available) ──────────────────
try:
    from aiokafka import AIOKafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    log.warning("aiokafka not installed — Kafka publishing disabled")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


# ── Telemetry generation ──────────────────────────────────────────────────────

class AssetState:
    """Tracks the rolling sensor state for one asset with Gaussian drift."""

    def __init__(self, asset: AssetConfig):
        self.asset = asset
        # Initialise mid-range values
        self._values: Dict[str, float] = {
            name: (sr.normal_min + sr.normal_max) / 2.0
            for name, sr in asset.sensors.items()
        }
        self._fault_active: Optional[str] = None
        self._fault_step: int = 0

    def _drift(self, name: str, sr: SensorRange) -> float:
        """Apply small Gaussian drift + mean reversion to keep values realistic."""
        current = self._values[name]
        mid = (sr.normal_min + sr.normal_max) / 2.0
        spread = (sr.normal_max - sr.normal_min) / 2.0

        # Mean reversion pulls value back toward normal centre
        reversion = 0.05 * (mid - current)
        noise = random.gauss(0, spread * 0.015)
        new_val = current + reversion + noise

        # Hard clamp to physical limits
        new_val = max(sr.min_val, min(sr.max_val, new_val))
        self._values[name] = new_val
        return new_val

    def inject_fault(self, fault_name: str):
        """Begin injecting a fault signature into this asset."""
        if fault_name not in FAULT_SIGNATURES:
            raise ValueError(f"Unknown fault: {fault_name}")
        self._fault_active = fault_name
        self._fault_step = 0
        log.warning(f"[FAULT INJECTED] {self.asset.asset_id} — {fault_name}: "
                    f"{FAULT_SIGNATURES[fault_name]['description']}")

    def clear_fault(self):
        self._fault_active = None
        self._fault_step = 0

    def read(self) -> Dict[str, float]:
        """Return one sensor reading snapshot, applying fault if active."""
        readings: Dict[str, float] = {}

        for name, sr in self.asset.sensors.items():
            val = self._drift(name, sr)

            if self._fault_active:
                sig = FAULT_SIGNATURES[self._fault_active]
                if name == sig["sensor"]:
                    # Ramp the fault effect over ramp_steps ticks
                    ramp_steps = sig["ramp_steps"]
                    progress = min(self._fault_step / ramp_steps, 1.0)
                    multiplier = 1.0 + (sig["multiplier"] - 1.0) * progress
                    val = val * multiplier
                    val = max(sr.min_val, min(sr.max_val, val))

            readings[name] = round(val, 3)

        if self._fault_active:
            self._fault_step += 1

        return readings

    def anomaly_score(self, readings: Dict[str, float]) -> float:
        """
        Heuristic anomaly score 0.0–1.0 based on how far readings are
        from normal range. >0.85 triggers an alert.
        """
        scores = []
        for name, sr in self.asset.sensors.items():
            val = readings[name]
            span = sr.max_val - sr.min_val
            if span == 0:
                continue
            normal_centre = (sr.normal_min + sr.normal_max) / 2.0
            deviation = abs(val - normal_centre) / (span / 2.0)
            scores.append(min(deviation, 1.0))
        return round(sum(scores) / len(scores), 4) if scores else 0.0


def build_telemetry_frame(state: AssetState) -> dict:
    """Build a complete telemetry JSON frame for one asset."""
    readings = state.read()
    score = state.anomaly_score(readings)
    asset = state.asset

    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "asset_id": asset.asset_id,
        "gdc_id": asset.gdc_id,
        "asset_type": asset.asset_type,
        "location": asset.location,
        "criticality": asset.criticality,
        "sensors": readings,
        "anomaly_score": score,
        "fault_active": state._fault_active,
        "status": (
            "CRITICAL" if score > 0.85 else
            "WARNING"  if score > 0.60 else
            "NORMAL"
        ),
    }


# ── Kafka producer ────────────────────────────────────────────────────────────

async def make_producer() -> Optional["AIOKafkaProducer"]:
    if not KAFKA_AVAILABLE:
        return None
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            compression_type="gzip",
        )
        await producer.start()
        log.info(f"Kafka producer connected → {KAFKA_BOOTSTRAP}")
        return producer
    except Exception as e:
        log.warning(f"Kafka unavailable ({e}) — stdout-only mode")
        return None


# ── Main simulation loop ───────────────────────────────────────────────────────

async def simulate(
    asset_ids: list[str],
    demo_mode: bool,
    demo_fault: str,
    demo_delay_s: int,
    no_kafka: bool,
    interval: float = TELEMETRY_INTERVAL_S,
):
    states = {aid: AssetState(get_asset(aid)) for aid in asset_ids}
    producer = None if no_kafka else await make_producer()

    log.info(f"Simulating {len(states)} asset(s) at {interval}s intervals")
    if demo_mode:
        log.info(f"Demo mode: fault '{demo_fault}' on {DEMO_ASSET_ID} in {demo_delay_s}s")

    start_time = time.monotonic()

    try:
        while True:
            tick_start = time.monotonic()
            elapsed = tick_start - start_time

            # Demo fault injection
            if demo_mode and elapsed >= demo_delay_s:
                state = states.get(DEMO_ASSET_ID)
                if state and not state._fault_active:
                    state.inject_fault(demo_fault)

            for aid, state in states.items():
                frame = build_telemetry_frame(state)

                # Always print to stdout
                print(json.dumps(frame, separators=(",", ":")))

                # Publish to Kafka if available
                if producer:
                    await producer.send(KAFKA_TOPIC_TELEMETRY, frame)

            # Sleep for remainder of interval
            elapsed_tick = time.monotonic() - tick_start
            sleep_for = max(0.0, interval - elapsed_tick)
            await asyncio.sleep(sleep_for)

    except asyncio.CancelledError:
        log.info("Simulation cancelled — shutting down")
    finally:
        if producer:
            await producer.stop()
            log.info("Kafka producer closed")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="OTDT Sensor Simulator — GDC Kenya")
    p.add_argument("--asset", type=str, default=None,
                   help="Simulate single asset ID (e.g. WP-07). Default: all 50.")
    p.add_argument("--demo", action="store_true",
                   help="Enable demo mode: inject fault on WP-07 after --delay seconds")
    p.add_argument("--fault", type=str, default="bearing_wear",
                   choices=list(FAULT_SIGNATURES.keys()),
                   help="Fault type for demo mode (default: bearing_wear)")
    p.add_argument("--delay", type=int, default=30,
                   help="Seconds before fault injection in demo mode (default: 30)")
    p.add_argument("--no-kafka", action="store_true",
                   help="Disable Kafka publishing — stdout only")
    p.add_argument("--interval", type=float, default=TELEMETRY_INTERVAL_S,
                   help=f"Telemetry publish interval in seconds (default: {TELEMETRY_INTERVAL_S})")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.asset:
        try:
            asset_ids = [get_asset(args.asset).asset_id]
        except KeyError as e:
            print(f"Error: {e}")
            raise SystemExit(1)
    else:
        asset_ids = list(ASSETS.keys())

    if args.demo and DEMO_ASSET_ID not in asset_ids:
        asset_ids.append(DEMO_ASSET_ID)

    try:
        asyncio.run(simulate(
            asset_ids=asset_ids,
            demo_mode=args.demo,
            demo_fault=args.fault,
            demo_delay_s=args.delay,
            no_kafka=args.no_kafka,
            interval=args.interval,
        ))
    except KeyboardInterrupt:
        log.info("Stopped by user")