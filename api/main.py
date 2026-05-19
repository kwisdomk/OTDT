from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import asyncio
from typing import List
from dotenv import load_dotenv

# Local imports
from api.db.timescale import init_schema, store_reading
from api.db.redis_client import set_asset_state, get_all_asset_states
from api.anomaly.detector import detector
from api.routers import whatif, maximo, twin, assets, monte_carlo, sensors, agent, watsonx, anomaly, predict

# Monte Carlo integration
from monte_carlo.engine import run_simulation

# Optional integrations (may not exist yet)
try:
    from api.integrations.kafka_consumer import consume
except ImportError:
    async def consume(handler):
        """Mock Kafka consumer for development."""
        pass

try:
    from api.integrations.maximo_client import create_work_order
except ImportError:
    def create_work_order(asset_id, prob, scheduled_date):
        """Mock work order creation."""
        return {"work_order_id": f"WO-{asset_id}-MOCK"}

load_dotenv()


# ── WebSocket Connection Manager ───────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.disconnect(connection)


manager = ConnectionManager()


# ── Kafka message handler ─────────────────────────────────────────────
async def handle_message(msg: dict):
    """Process each incoming sensor reading from Kafka."""
    asset_id = msg.get("asset_id", "WP-07")
    sensors = msg.get("sensors", {}) or {}
    timestamp = msg.get("timestamp", "")

    # 1. Store in TimescaleDB
    await store_reading(asset_id, sensors, timestamp)

    # 2. Run anomaly detection
    status, score = detector.predict(sensors)

    # 3. Monte Carlo when anomaly detected
    mc_result = None
    work_order_id = None

    if score > 0.5:
        mc_result = run_simulation(sensors) or {}
        prob = float(mc_result.get("failure_probability", 0.0))
        if prob > 0.25:
            wo = create_work_order(asset_id, prob, mc_result.get("optimal_maintenance_day"))
            if isinstance(wo, dict):
                work_order_id = wo.get("work_order_id")
    else:
        # Provide a consistent payload even when MC isn't run
        mc_result = {
            "failure_probability": 0.0,
            "days_to_failure_p50": None,
            "recommended_action": "MONITOR",
            "optimal_maintenance_day": None,
        }

    colour = "#C00000" if status == "CRITICAL" else ("#FF9900" if status == "WARNING" else "#1E6B3C")

    state = {
        "asset_id": asset_id,
        "asset_label": f"GDC-{asset_id}",
        "status": status,
        "colour_hex": colour,
        "sensors": sensors,
        "anomaly_score": round(float(score), 4),
        "failure_probability": mc_result.get("failure_probability"),
        "days_to_failure_p50": mc_result.get("days_to_failure_p50"),
        "recommended_action": mc_result.get("recommended_action", "MONITOR"),
        "optimal_maintenance_day": mc_result.get("optimal_maintenance_day"),
        "active_work_order_id": work_order_id,
        "mc_result": mc_result,
        "timestamp": timestamp,
    }

    # 4. Cache in Redis
    await set_asset_state(asset_id, state)

    # 5. Broadcast to WebSocket clients
    all_assets = await get_all_asset_states()
    await manager.broadcast(
        {
            "timestamp": timestamp,
            "assets": all_assets,
            "synthetic": True,
        }
    )

    print(f"[Kafka] Processed {asset_id}: {status} (score={score})")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_schema()
    asyncio.create_task(consume(handle_message))
    print("[API] OT Digital Twin API started")
    yield
    # Shutdown
    print("[API] Shutting down")


# ── FastAPI App ───────────────────────────────────────────────────────
app = FastAPI(
    title="OT Digital Twin API",
    version="1.0.0",
    description="GDC Kenya — 50-asset geothermal digital twin",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assets.router,       prefix="/api",              tags=["Assets"])
app.include_router(monte_carlo.router,  prefix="/api/monte-carlo",  tags=["Monte Carlo"])
app.include_router(twin.router,         prefix="/api",              tags=["Digital Twin"])
app.include_router(sensors.router,      prefix="/api",              tags=["Sensors"])
app.include_router(whatif.router,       prefix="/whatif",           tags=["What-If Analysis"])
app.include_router(maximo.router,       prefix="/maximo",           tags=["Maximo"])
app.include_router(watsonx.router,      prefix="/api/watsonx",      tags=["IBM watsonx.ai"])
app.include_router(agent.router,        prefix="/api",              tags=["Agent Integration"])
app.include_router(anomaly.router,      prefix="/api",              tags=["CNN Anomaly"])       # Track B – Step 7
app.include_router(predict.router,      prefix="/api",              tags=["LSTM Prediction"])   # Track B – Step 4


# ── Health & Status Endpoints ──────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ot-digital-twin", "synthetic": True}


@app.get("/status")
async def status():
    return {
        "active": os.getenv("SYSTEM_ACTIVE", "true") == "true",
        "demo_mode": os.getenv("DEMO_MODE", "false") == "true",
        "version": "1.0.0",
        "synthetic": True,
    }


@app.get("/disclaimer")
async def disclaimer():
    return {
        "synthetic": True,
        "notice": "SYNTHETIC DATA: All sensor readings and AI predictions are generated from simulation models. Not real plant data.",
        "partner": "i3 Technologies Ltd | IBM Silver Partner | CEID: 7sq30",
    }


# ── Anomaly Test Endpoint ──────────────────────────────────────────────
@app.get("/anomaly/test")
async def test_anomaly():
    """Test anomaly detection with sample data."""
    try:
        sample_sensors = {
            "temperature_c": 185.0,
            "pressure_bar": 25.0,
            "vibration_mms": 4.2,
            "flow_rate_ls": 85.0,
        }
        status, score = detector.predict(sample_sensors)
        return {
            "status": status,
            "anomaly_score": score,
            "sensors": sample_sensors,
            "synthetic": True,
        }
    except Exception as e:
        return {"error": str(e), "message": "Anomaly detector not available"}


# ── Sensor Endpoint (Mock) ────────────────────────────────────────────
@app.get("/sensors/latest")
async def sensors_latest():
    """Get latest readings (mock data for now)."""
    return {
        "assets": [
            {
                "asset_id": "WP-07",
                "asset_label": "GDC-WP-007",
                "status": "NORMAL",
                "sensors": {
                    "temperature_c": 185.0,
                    "pressure_bar": 25.0,
                    "vibration_mms": 4.2,
                    "flow_rate_ls": 85.0,
                },
                "anomaly_score": 0.12,
                "failure_probability": 0.08,
                "synthetic": True,
            }
        ]
    }


# ── WebSocket Singletons (created once, not per-tick) ─────────────────────
# Initialise at module level so the WebSocket handler doesn't rebuild them
# every 2 seconds (was causing Excel reads on every broadcast tick).
try:
    from maximo.monitor_client import MaximoMonitorClient as _MonitorClient
    from maximo.asset_loader import AssetLoader as _AssetLoader
    _ws_loader = _AssetLoader(mock_mode=True)
    _ws_loader.load_from_excel()
    _ws_client = _MonitorClient(mock_mode=True)
    print(f"[WS] Asset loader ready — {len(_ws_loader.assets)} assets")
except Exception as e:
    _ws_loader = None
    _ws_client = None
    print(f"[WS] Asset loader unavailable: {e} — WebSocket will use Redis cache only")


# ── WebSocket Endpoint ─────────────────────────────────────────────────
@app.websocket("/twin/stream")
async def websocket_stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            import datetime as _dt

            # Try Redis cache first (populated by Kafka pipeline)
            cached = await get_all_asset_states()
            if cached:
                await websocket.send_json({
                    "timestamp": _dt.datetime.now().isoformat(),
                    "assets": cached,
                    "synthetic": True,
                    "disclaimer": "SYNTHETIC DATA: Computer-generated"
                })
            elif _ws_loader and _ws_client:
                # Fallback: build payload from mock asset loader (no Kafka)
                assets_payload = []
                for asset in _ws_loader.assets:
                    asset_id = asset["asset_id"]
                    sensors = _ws_client.get_latest_sensors(asset_id)
                    is_demo_asset = asset_id in ("GDC-WP-007", "WP-007")
                    status = "WARNING" if is_demo_asset else "NORMAL"
                    colour = "#FFA500" if is_demo_asset else "#1E6B3C"
                    assets_payload.append({
                        "asset_id": asset_id,
                        "asset_label": asset.get("asset_label", asset_id),
                        "status": status,
                        "colour_hex": colour,
                        "health_score": sensors.get("health_score", 92.0),
                        "failure_probability": 0.34 if is_demo_asset else 0.08,
                        "recommended_action": "SCHEDULE_MAINTENANCE" if is_demo_asset else "MONITOR",
                        "sensors": {
                            "bearing_temp_c": sensors.get("temperature_c", 83.0),
                            "bearing_vibration_mms": sensors.get("vibration_mm_s", 4.2),
                            "steam_inlet_pressure_bar": sensors.get("pressure_bar", 68.0),
                        },
                        "synthetic": True,
                    })
                await websocket.send_json({
                    "timestamp": _dt.datetime.now().isoformat(),
                    "assets": assets_payload,
                    "synthetic": True,
                    "disclaimer": "SYNTHETIC DATA: Computer-generated"
                })

            await asyncio.sleep(2)
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
