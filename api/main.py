from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import List
from kafka import KafkaConsumer
import threading
import time

app = FastAPI(title="OT Digital Twin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()
loop = None

def run_kafka_consumer():
    global loop
    print("[Kafka] Starting consumer...")
    consumer = KafkaConsumer(
        'sensor.telemetry',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        group_id='otdt-api'
    )
    print("[Kafka] Connected. Waiting for messages...")
    
    for msg in consumer:
        data = msg.value
        asset_id = data.get('asset_id', 'unknown')
        sensors = data.get('sensors', {})
        vib = sensors.get('vibration_mms', 'N/A')
        print(f"[Kafka] Received: {asset_id} - vib={vib}")
        
        # Broadcast to WebSocket clients
        if loop:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast({
                    "timestamp": data.get("timestamp"),
                    "assets": [{
                        "asset_id": asset_id,
                        "asset_label": asset_id,
                        "status": "NORMAL",
                        "sensors": sensors,
                        "anomaly_score": 0.12,
                        "failure_probability": 0.08,
                        "days_to_failure_p50": 45,
                        "recommended_action": "MONITOR",
                        "active_work_order_id": None
                    }],
                    "synthetic": True
                }),
                loop
            )

@app.on_event("startup")
async def startup():
    global loop
    loop = asyncio.get_event_loop()
    print("[API] Starting Kafka consumer thread")
    thread = threading.Thread(target=run_kafka_consumer, daemon=True)
    thread.start()
    print("[API] Startup complete")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ot-digital-twin"}

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