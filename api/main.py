"""
OT Digital Twin — FastAPI Backend
Complete REST API + WebSocket server for 50 GDC geothermal assets.

Endpoints:
    GET  /health                 — service health
    GET  /status                 — system status (active/demo)
    GET  /disclaimer             — synthetic data notice
    GET  /sensors/latest         — latest readings for all assets
    GET  /sensors/{asset_id}     — latest for single asset
    WS   /twin/stream            — WebSocket live stream
    POST /whatif/simulate        — what-if analysis
    GET  /maximo/alerts          — active Maximo alerts

Author: Wisdom Kinoti / i3 Technologies
Based on: Solo Build Guide Part 6.7
"""

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add parent directory to path for monte_carlo imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# ── Local imports (will be created next) ──────────────────────────────
from api.db.timescale import init_schema, store_reading, latest_readings
from api.db.redis_client import set_asset_state, get_all_asset_states, get_asset_state
from api.anomaly.detector import detector
from api.integrations.kafka_consumer import consume
from api.integrations.maximo_client import create_work_order, get_active_alerts

# ── Monte Carlo engine (from sibling monte_carlo directory) ───────────
try:
    import importlib.util
    import pathlib
    mc_path = pathlib.Path(__file__).parent.parent / "monte_carlo" / "engine.py"
    spec = importlib.util.spec_from_file_location("engine", mc_path)
    mc_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mc_mod)
    run_simulation = mc_mod.run_simulation
    MC_AVAILABLE = True
except Exception as e:
    print(f"[WARN] Monte Carlo engine not available: {e}")
    MC_AVAILABLE = False
    def run_simulation(sensors, n=10000): return {"failure_probability": 0.0, "error": "MC not loaded"}

# ── Configuration ──────────────────────────────────────────────────────
MC_THRESHOLD = float(os.getenv("FAILURE_PROBABILITY_ALERT_THRESHOLD", 0.25))
DISCLAIMER = "SYNTHETIC DATA: All sensor readings and AI predictions are generated from simulation models. Not real plant data."

# ── WebSocket Connection Manager ───────────────────────────────────────
class WSManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.connections:
            try:
                await ws.send_json(data)
            except:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

manager = WSManager()

# ── Kafka Message Handler ──────────────────────────────────────────────
async def handle_telemetry(msg: dict):
    """Process each incoming sensor reading from Kafka."""
    asset_id = msg.get("asset_id", "WP-07")
    sensors = msg.get("sensors", {})
    timestamp = msg.get("timestamp", "")

    # 1. Store in TimescaleDB
    await store_reading(asset_id, sensors, timestamp)

    # 2. Run anomaly detection
    status, score = detector.predict(sensors)

    # 3. Run Monte Carlo if anomaly score > 0.5
    mc_result = {}
    work_order_id = None
    if score > 0.5 and MC_AVAILABLE:
        # Add asset_id to sensor_state for Monte Carlo
        sensor_state = {**sensors, "asset_id": asset_id}
        mc_result = run_simulation(sensor_state)
        prob = mc_result.get("failure_probability", 0.0)

        # 4. Auto-create Maximo work order if probability exceeds threshold
        if prob > MC_THRESHOLD:
            opt_day = mc_result.get("optimal_maintenance_day", "")
            wo = create_work_order(asset_id, prob, opt_day)
            work_order_id = wo.get("work_order_id")

    # 5. Build asset state for Redis + WebSocket
    colour = "#C00000" if status == "CRITICAL" else ("#FF9900" if status == "WARNING" else "#1E6B3C")

    state = {
        "asset_id": asset_id,
        "asset_label": msg.get("gdc_id", f"GDC-{asset_id}"),
        "status": status,
        "colour_hex": colour,
        "sensors": sensors,
        "anomaly_score": round(score, 4),
        "failure_probability": mc_result.get("failure_probability", 0.0),
        "days_to_failure_p50": mc_result.get("days_to_failure_p50"),
        "recommended_action": mc_result.get("recommended_action", "MONITOR"),
        "active_work_order_id": work_order_id,
        "timestamp": timestamp,
    }

    # 6. Cache in Redis
    await set_asset_state(asset_id, state)

    # 7. Broadcast to all WebSocket clients
    all_assets = await get_all_asset_states()
    await manager.broadcast({
        "timestamp": timestamp,
        "assets": all_assets,
        "synthetic": True,
        "disclaimer": DISCLAIMER,
    })

# ── FastAPI Lifespan ───────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_schema()
    asyncio.create_task(consume(handle_telemetry))
    print(f"[API] OT Digital Twin started | Monte Carlo: {'OK' if MC_AVAILABLE else 'DISABLED'}")
    yield
    # Shutdown
    print("[API] Shutting down")

# ── FastAPI App ────────────────────────────────────────────────────────
app = FastAPI(
    title="OT Digital Twin API",
    version="1.0.0",
    lifespan=lifespan,
    description="GDC Kenya — 50-asset geothermal digital twin with Monte Carlo failure prediction"
)

# CORS — allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health & Status Endpoints ──────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ot-digital-twin", "synthetic": True}

@app.get("/status")
async def status():
    return {
        "active": os.getenv("SYSTEM_ACTIVE", "true") == "true",
        "demo_mode": os.getenv("DEMO_MODE", "false") == "true",
        "monte_carlo": MC_AVAILABLE,
        "version": "1.0.0",
        "synthetic": True,
    }

@app.get("/disclaimer")
async def disclaimer():
    return {
        "synthetic": True,
        "notice": DISCLAIMER,
        "version": "1.0.0",
        "contact": "events@i3technologies.co.ke",
        "partner": "i3 Technologies Ltd | IBM Silver Partner | CEID: 7sq30",
    }

# ── Sensor Endpoints ───────────────────────────────────────────────────
@app.get("/sensors/latest")
async def sensors_latest():
    """Get latest readings for all assets (from Redis cache)."""
    return await get_all_asset_states()

@app.get("/sensors/{asset_id}")
async def sensor_by_id(asset_id: str):
    """Get latest reading for a specific asset."""
    state = await get_asset_state(asset_id)
    if not state:
        return {"error": f"Asset {asset_id} not found in cache", "asset_id": asset_id}
    return state

# ── What-If Endpoint ───────────────────────────────────────────────────
from pydantic import BaseModel

class WhatIfRequest(BaseModel):
    asset_id: str
    maintenance_date: str  # ISO format YYYY-MM-DD

@app.post("/whatif/simulate")
async def whatif_simulate(req: WhatIfRequest):
    """Simulate failure probability if maintenance done on given date."""
    state = await get_asset_state(req.asset_id)
    if not state:
        return {"error": f"Asset {req.asset_id} not in cache"}
    if not MC_AVAILABLE:
        return {"error": "Monte Carlo engine not available"}
    try:
        result = mc_mod.whatif_simulation(state["sensors"], req.maintenance_date)
        return result
    except Exception as e:
        return {"error": str(e)}

# ── Maximo Endpoint ────────────────────────────────────────────────────
@app.get("/maximo/alerts")
async def maximo_alerts():
    """Get active Maximo Monitor alerts."""
    return get_active_alerts()

# ── WebSocket Endpoint ─────────────────────────────────────────────────
@app.websocket("/twin/stream")
async def websocket_stream(websocket: WebSocket):
    """WebSocket endpoint for live asset state updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, ignore client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ── Run with uvicorn ───────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True,
    )