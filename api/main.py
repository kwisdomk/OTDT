from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from dotenv import load_dotenv
from typing import List

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="OT Digital Twin API",
    version="1.0.0",
    description="GDC Kenya — 50-asset geothermal digital twin"
)

# CORS middleware
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
        from anomaly.detector import detector
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
            "synthetic": True
        }
    except Exception as e:
        return {"error": str(e), "message": "Anomaly detector not available"}

# ── Simple Sensor Endpoint (Mock) ──────────────────────────────────────
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
                    "flow_rate_ls": 85.0
                },
                "anomaly_score": 0.12,
                "failure_probability": 0.08,
                "synthetic": True
            }
        ]
    }

# ── WebSocket Manager (Simple Version) ─────────────────────────────────
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
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/twin/stream")
async def websocket_stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send a heartbeat every 5 seconds
            await asyncio.sleep(5)
            await websocket.send_json({
                "timestamp": "2026-03-26T00:00:00",
                "assets": [{"asset_id": "WP-07", "status": "NORMAL"}],
                "synthetic": True
            })
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
