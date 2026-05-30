# OT Digital Twin (OTDT)

**Agentic AI Operating Layer for Geothermal Critical Infrastructure**

> ⚠️ **SYNTHETIC DATA**: All sensor readings and AI predictions are generated from simulation models. Not real plant data.
>
> **PRODUCT BASELINE**: Development must conform to the original March 2026
> OTDT source artifacts. Read [docs/product_baseline.md](docs/product_baseline.md)
> and [docs/Decision Log.md](docs/Decision%20Log.md) before changing
> product scope, architecture claims, demo figures or status.

Real-time industrial digital twin for geothermal plant operations — Monte Carlo failure prediction, LSTM anomaly detection, and live Unity XR visualisation. Built on IBM Maximo MAS 9.1 + watsonx.ai + Red Hat OpenShift.

**East Africa Agentic AI Workshop 2026 — IEEE IES East Africa Industrial Innovation Summit**

---

## Architecture Overview

```
Physical Sensors → Watson IoT → Kafka → API (FastAPI)
                                          ├── TimescaleDB (time-series storage)
                                          ├── Redis (real-time state cache)
                                          ├── Anomaly Detector → Monte Carlo Engine
                                          │                       └── Maximo Work Orders
                                          └── WebSocket → React Dashboard / Unity XR
```

## Five AI Agents

| Agent | Description | Model |
|---|---|---|
| **Failure Predictor** | LSTM model trained on 5-year sensor history. Predicts failure probability over 30/60/90-day windows | LSTM (3-layer, 64 units) |
| **Monte Carlo Sim Engine** | 10,000 Weibull-distributed failure scenarios against live sensor readings | NumPy + SciPy |
| **What-If Analyst** | Interactive maintenance deferral slider — quantifies risk of deferral decisions in real time | Monte Carlo + cost model |
| **Anomaly AI** | CNN visual anomaly detection on 3D digital twin screenshots | ResNet-18 fine-tuned |
| **Maintenance Scheduler** | Converts failure curves into optimised inspection schedules | Priority queue + LP |

## Quick Start

### Docker Compose (recommended)

```bash
docker-compose up --build
```

Services:
- **API**: http://localhost:8000 (FastAPI + Swagger at `/docs`)
- **Dashboard**: http://localhost:3000 (React)
- **Kafka**: localhost:9092 (internal), localhost:29092 (external)
- **TimescaleDB**: localhost:5432
- **Redis**: localhost:6379

### Local Development

```bash
# API
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Sensor Simulator
cd sensor_simulator
python kafka_publisher.py --demo

# Frontend
cd frontend/react-dashboard
npm install && npm start
```

## Project Structure

```
OTDT/
├── api/                    # FastAPI application
│   ├── main.py             # App entry point, WebSocket, Kafka consumer
│   ├── routers/            # Route handlers (whatif, anomaly, predict, assets, etc.)
│   ├── anomaly/            # Rule-based anomaly detector
│   ├── db/                 # TimescaleDB + Redis clients
│   └── integrations/       # Kafka consumer, Maximo client
├── monte_carlo/            # Weibull-based MC simulation engine
│   └── engine.py           # run_simulation() + whatif_simulation()
├── ml/                     # Machine learning models
│   ├── lstm/               # LSTM failure predictor (Step 4)
│   └── cnn_anomaly/        # CNN visual anomaly detector (Step 7)
├── sensor_simulator/       # Geothermal sensor telemetry simulator
├── scheduler/              # Maintenance schedule optimizer (Step 8)
├── maximo/                 # IBM Maximo MAS integration layer
├── frontend/react-dashboard/  # React monitoring dashboard
├── unity/
│   ├── GDC_Plant_Twin/     # Unity XR 3D digital twin
│   └── ThreeJS_Viewer/     # Browser-based 3D fallback
├── datasets/               # GDC Kenya synthetic datasets (Excel)
├── docker-compose.yml      # Full stack orchestration
└── requirements.txt        # Python dependencies
```

## Demo Scenarios

1. **Failure Prediction**: WP-07 shows 34% failure probability within 30 days — current calendar schedule wouldn't inspect for 45 days
2. **What-If Analysis**: Defer maintenance slider 0→45 days, probability rises 34%→68%, expected cost USD 122,400
3. **Optimised Schedule**: 90-day schedule highlighting 3 unplanned high-risk assets

## Key Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `GET` | `/api/assets` | All 50 GDC geothermal assets |
| `GET` | `/api/twins/{asset_id}/sensors/latest` | Latest sensor readings |
| `POST` | `/api/monte-carlo/simulate` | Run 10k Monte Carlo simulation |
| `POST` | `/whatif/simulate-days` | What-If deferral analysis |
| `GET` | `/api/anomaly/status` | CNN anomaly scores (all assets) |
| `POST` | `/api/predict/failure` | LSTM failure probability |
| `WS` | `/twin/stream` | Real-time WebSocket feed |

## Technology Stack

**IBM**: Maximo MAS 9.1 APM · Watson IoT · Watson Studio ML · watsonx.ai · Event Streams (Kafka) · Red Hat OpenShift

**Core**: Python 3.11 · FastAPI · NumPy · SciPy · TensorFlow · Kafka · TimescaleDB · Redis

**Visualisation**: React · Unity Pro 2023.2 LTS · Three.js

## Target Client

GDC Kenya (geothermal) — 180 wells, 50 modelled assets. ROI: 650%+ (preventing 2 unplanned pump failures/year saves USD 360,000 vs. USD 48,000 platform cost).

---

*i3 Technologies Ltd | IBM Silver Partner CEID 7sq30 | Philip Mukiti | 2026*
