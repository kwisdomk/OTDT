# OTDT - OT Digital Twin Platform 🛢️🔬

![OTDT Banner](https://via.placeholder.com/1200x400/1e3a8a/ffffff?text=OT+Digital+Twin+-+GDC+Kenya)

**Real-time industrial digital twin for geothermal wellpad operations** — featuring Monte Carlo failure prediction, LSTM anomaly detection, Kafka streaming, and live React dashboard (Unity XR ready). Built for IBM Maximo MAS + watsonx.ai ecosystem.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.x-61DAFB?style=flat&logo=react)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://docker.com)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-7.6-231F20?style=flat&logo=apachekafka)](https://kafka.apache.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://python.org)
[![License](https://img.shields.io/github/license/kwisdomk/OTDT?style=flat)](LICENSE)

**Demo Context**: Geothermal Development Company (GDC) Kenya — 50+ wellpads (WP-07 etc.). *Synthetic data for workshop demo.*

## 📋 Features

| Feature | Description | Endpoint |
|---------|-------------|----------|
| **Live Twin Streaming** | WebSocket real-time asset states | `ws://localhost:8000/twin/stream` |
| **Anomaly Detection** | LSTM/TensorFlow vibration+temp analysis | `/anomaly/test` |
| **Monte Carlo Simulation** | Failure probability & maintenance timing | Auto-triggered on anomalies |
| **What-If Analysis** | Sensor override predictions | `/whatif/` |
| **Maximo Integration** | Auto work order creation | Internal |
| **Data Pipeline** | Kafka -> Redis -> TimescaleDB | `docker-compose up -d` |
| **React Dashboard** | Live charts, asset status, MC results | `npm start` |
| **Sensor Simulator** | Synthetic geothermal data (Kafka/WatsonIoT) | `python simulator.py` |

## 🏗️ Architecture

```
Sensors (Simulated) ──[Kafka]──> API (FastAPI)
                            │
                            ├─[LSTM Anomaly]──┐
                            │                 │
                            ├─[Monte Carlo]───┼──> Redis/TimescaleDB
                            │                 │
                            └─[Maximo WO]─────┘
                                          │
                                   WebSocket ──> React Dashboard (Unity XR)
```

## 🚀 Quickstart (5 minutes)

1. **Clone & Backend** (root dir)
   ```bash
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   Test: `curl http://localhost:8000/health` → `{"status": "ok"}`

2. **Services** (Docker)
   ```bash
   docker-compose up -d  # Kafka, TimescaleDB, Redis, Zookeeper
   ```

3. **Sensors**
   ```bash
   python sensor_simulator/simulator.py  # Publishes to Kafka
   ```

4. **Frontend**
   ```bash
   cd frontend/react-dashboard
   npm install && npm start  # http://localhost:3000
   ```

**Full docs**: http://localhost:8000/docs

## 📁 Project Structure

```
OTDT/
├── main.py                 # FastAPI entrypoint (root uvicorn)
├── api/                    # Backend routers + anomaly/ML
│   ├── routers/            # sensors, twin, whatif, maximo, montecarlo
│   ├── anomaly/detector.py # LSTM
│   ├── db/                 # Redis + Timescale
│   └── integrations/       # Kafka consumer + Maximo
├── sensor_simulator/       # Synthetic data publisher
├── monte_carlo/            # Failure prediction engine
├── frontend/react-dashboard/ # Live dashboard
├── docker-compose.yml      # Kafka/Redis/DBs
└── requirements.txt
```

## 🔧 Detailed Setup

### Environment Variables (.env)
```
API_HOST=0.0.0.0
API_PORT=8000
DEMO_MODE=true
SYSTEM_ACTIVE=true
# DB: POSTGRES_* in docker-compose.yml
# Kafka: localhost:9092
# Redis: localhost:6379
```

### Ports
- API: 8000 (FastAPI docs: `/docs`, WebSocket: `/twin/stream`)
- Frontend: 3000
- Kafka: 9092
- TimescaleDB: 5432
- Redis: 6379

### Testing
```bash
# Health
curl http://localhost:8000/health

# Anomaly test
curl http://localhost:8000/anomaly/test

# Disclaimer (synthetic data notice)
curl http://localhost:8000/disclaimer
```

## 📚 API Reference
- **Swagger UI**: http://localhost:8000/docs
- **WebSocket**: Connect to `/twin/stream` for live `{"assets": [...], "timestamp": "..."}`
- **Key Payload**:
  ```json
  {
    "asset_id": "WP-07",
    "status": "WARNING",
    "anomaly_score": 0.75,
    "failure_probability": 0.32,
    "recommended_action": "MAINTAIN",
    "colour_hex": "#FF9900"
  }
  ```

## 🤝 Contributing
1. Fork & PR
2. `pre-commit install` (add later)
3. Tests: `pytest` (add later)

**Workshop**: East Africa Agentic AI 2026 | IBM Research Lab Africa | i3 Technologies Ltd

---

*Synthetic demo data. Production deployment: OpenShift + MAS 9.1 + watsonx.ai*

[![Star History](https://img.shields.io/github/stars/kwisdomk/OTDT?style=social)](https://github.com/kwisdomk/OTDT)
