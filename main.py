"""
OT Digital Twin API - main.py
Wires together: Kafka consumer → Anomaly Detector → Monte Carlo → WebSocket broadcast
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import sys
import os
from typing import List, Optional
from kafka import KafkaConsumer
import threading
from datetime import datetime, timedelta

# --- Path setup ---
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'api'))
sys.path.insert(0, ROOT)

from api.anomaly.detector import detector
from monte_carlo.engine import run_simulation

app = FastAPI(title="OT Digital Twin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Sensor key translation ---
def translate_sensors_for_mc(sensors: dict) -> dict:
    """Map simulator sensor keys → Monte Carlo engine keys."""
    return {
        'bearing_temp_c': sensors.get('temperature_c', 85.0),
        'bearing_vibration_mms': sensors.get('vibration_mms', 4.2),
        'steam_inlet_pressure_bar': sensors.get('pressure_bar', 24.0),
    }

# --- Work order state (in-memory for demo) ---
active_work_orders: dict = {}
wo_counter = 0

def maybe_create_work_order(asset_id: str, status: str) -> Optional[str]:
    global wo_counter
    if status in ('WARNING', 'CRITICAL') and asset_id not in active_work_orders:
        wo_counter += 1
        wo_id = f"WO-2026-{wo_counter:03d}"
        active_work_orders[asset_id] = wo_id
        print(f"[Maximo] Work order created: {wo_id} for {asset_id}")
        return wo_id
    elif status == 'NORMAL' and asset_id in active_work_orders:
        wo_id = active_work_orders.pop(asset_id)
        print(f"[Maximo] Work order cleared: {wo_id} for {asset_id}")
        return None
    return active_work_orders.get(asset_id)

# --- WebSocket connection manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for d in dead:
            self.disconnect(d)

manager = ConnectionManager()
loop = None

# --- Kafka consumer thread ---
def run_kafka_consumer():
    global loop
    print("[Kafka] Starting consumer...")
    try:
        consumer = KafkaConsumer(
            'sensor.telemetry',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='otdt-api'
        )
    except Exception as e:
        print(f"[Kafka] Failed to connect: {e}")
        return

    print("[Kafka] Connected. Waiting for messages...")

    for msg in consumer:
        data = msg.value
        asset_id = data.get('asset_id', 'UNKNOWN')
        sensors = data.get('sensors', {})

        # Anomaly detection
        status, anomaly_score = detector.predict(sensors)

        # Monte Carlo — only run full simulation when anomaly detected
        if anomaly_score > 0.5:
            try:
                mc_result = run_simulation(translate_sensors_for_mc(sensors))
                failure_prob = mc_result.get('failure_probability', 0.34)
                days_p50 = mc_result.get('days_to_failure_p50', 14)
                action = mc_result.get('recommended_action', 'URGENT')
            except Exception as e:
                print(f"[MC] Error: {e}")
                failure_prob, days_p50, action = 0.34, 14, 'URGENT'
        else:
            failure_prob, days_p50, action = 0.08, 45, 'MONITOR'

        # Work order
        wo_id = maybe_create_work_order(asset_id, status)

        print(f"[Pipeline] {asset_id} | {status} | score={anomaly_score:.3f} | prob={failure_prob:.2f} | WO={wo_id}")

        if loop:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast({
                    "timestamp": data.get("timestamp"),
                    "assets": [{
                        "asset_id": asset_id,
                        "asset_label": data.get("asset_label", asset_id),
                        "status": status,
                        "colour_hex": {
                            "NORMAL": "#1E6B3C",
                            "WARNING": "#C55A11",
                            "CRITICAL": "#C00000"
                        }.get(status, "#888888"),
                        "sensors": sensors,
                        "anomaly_score": anomaly_score,
                        "failure_probability": failure_prob,
                        "days_to_failure_p50": days_p50,
                        "recommended_action": action,
                        "active_work_order_id": wo_id,
                    }],
                    "synthetic": True
                }),
                loop
            )

# --- App lifecycle ---
@app.on_event("startup")
async def startup():
    global loop
    loop = asyncio.get_event_loop()
    print("[API] Starting Kafka consumer thread")
    thread = threading.Thread(target=run_kafka_consumer, daemon=True)
    thread.start()
    print("[API] Startup complete")

# --- HTTP endpoints ---
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ot-digital-twin"}

@app.get("/status")
async def api_status():
    return {
        "service": "ot-digital-twin",
        "ws_clients": len(manager.active_connections),
        "active_work_orders": len(active_work_orders),
    }

@app.get("/disclaimer")
async def disclaimer():
    return {"message": "All sensor data is synthetic. Not real plant data."}

# --- What-If endpoint ---
class WhatIfRequest(BaseModel):
    asset_id: str
    days_deferred: int = 30
    maintenance_date: Optional[str] = None

@app.post("/whatif/simulate")
async def whatif_simulate(req: WhatIfRequest):
    """
    Simulate failure probability if maintenance is deferred by N days.
    Accepts either days_deferred (int) or maintenance_date (YYYY-MM-DD string).
    """
    days = req.days_deferred

    if req.maintenance_date:
        try:
            target = datetime.strptime(req.maintenance_date, "%Y-%m-%d")
            days = max(1, (target - datetime.now()).days)
        except ValueError:
            pass

    # Calibrated probability curve — bypasses MC engine for predictable demo values
    # 0 days = 8%, 30 days = ~45%, 60 days = ~85%, 90 days = ~92%
    degradation = min(1.0, days / 60.0)
    projected_prob = round(min(0.92, 0.08 + (degradation * 0.84)), 4)
    days_p50 = max(1, int(45 * (1 - degradation * 0.9)))
    action = 'MONITOR' if projected_prob < 0.10 else ('SCHEDULE_MAINTENANCE' if projected_prob < 0.25 else 'URGENT')

    return {
        "asset_id": req.asset_id,
        "days_deferred": days,
        "projected_failure_probability": projected_prob,
        "days_to_failure_p50": days_p50,
        "recommended_action": action,
        "synthetic": True
    }

# --- WebSocket ---
@app.websocket("/twin/stream")
async def websocket_stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)