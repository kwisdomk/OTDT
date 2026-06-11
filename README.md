# OT Digital Twin (OTDT)

Industrial digital twin prototype for geothermal asset monitoring, anomaly detection, Monte Carlo failure prediction, and real-time operational dashboards.

> **Public demo notice**
>
> - Synthetic data only
> - No real plant data
> - No production credentials
> - Demonstration prototype only
> - Not production-ready

## Overview

OTDT is an industrial digital twin demonstration prototype for operational technology monitoring and predictive maintenance. It models geothermal asset telemetry, streams simulated sensor readings through a local event pipeline, and exposes operational APIs for dashboard, simulation, and visualization clients.

The project is designed to show how a digital twin can combine real-time telemetry, failure-risk simulation, anomaly detection, maintenance planning concepts, and work-order integration patterns. The current implementation is intended for local demos, portfolio review, and technical evaluation, not for production operations.

All runtime data and demo outcomes in this repository are synthetic or simulated. The risk, cost, ROI, and maintenance examples are demonstration assumptions and simulation outputs, not verified results from a live plant.

## What It Demonstrates

- Real-time geothermal asset telemetry simulation
- Sensor data publishing through Kafka
- FastAPI operational API for assets, sensors, simulations, predictions, and integration endpoints
- Time-series storage and cache layer using TimescaleDB and Redis
- Monte Carlo failure-risk simulation
- What-if maintenance deferral analysis
- LSTM failure-prediction API path with fallback behavior
- Synthetic CNN-style anomaly scoring API for dashboard integration
- React operational dashboard
- Unity XR visualization project and Three.js viewer folder
- Maximo work-order adapter layer in mock/demo mode
- watsonx.ai natural-language what-if adapter in mock/configurable mode
- Local Docker Compose demo stack

## Architecture Overview

```text
Synthetic Sensor Simulator
        |
        v
      Kafka
        |
        v
FastAPI Operational API  <---------------- REST clients
        |
        +--> TimescaleDB time-series storage
        +--> Redis latest-state cache
        +--> Monte Carlo simulation engine
        +--> LSTM prediction API and fallback paths
        +--> Synthetic anomaly scoring API
        +--> Maximo adapter layer
        +--> watsonx.ai what-if adapter
        |
        +--> WebSocket stream: /twin/stream
                  |
                  +--> React dashboard
                  +--> Unity / 3D visualization clients
```

IBM and Red Hat platform components are represented as integration boundaries and demo-alignment concepts in this repository. Active cloud execution and production integration are not claimed by this README.

## Core Components

| Component | Purpose | Location |
| --- | --- | --- |
| FastAPI backend | Operational API, WebSocket stream, router orchestration, service startup | `api/` |
| Sensor simulator | Synthetic geothermal telemetry generation and Kafka publishing | `sensor_simulator/` |
| Monte Carlo engine | Failure-risk and maintenance deferral simulation logic | `monte_carlo/` |
| ML assets and scripts | LSTM and CNN anomaly model areas, including tracker-aligned LSTM artifacts where present | `ml/` |
| Scheduler | Maintenance scheduling and Gantt-related demo code | `scheduler/` |
| Maximo adapter | Asset loading, monitor mock client, and work-order client code | `maximo/` |
| React dashboard | Browser dashboard for operational demo views | `frontend/react-dashboard/` |
| Unity twin | Unity XR plant twin project | `unity/GDC_Plant_Twin/` |
| Three.js viewer | Browser-based 3D viewer area | `unity/ThreeJS_Viewer/` |
| Datasets | Synthetic workbook data and demo datasets | `datasets/` |
| Deployment assets | Deployment-related configuration and manifests | `deployment/` |
| Architecture docs | Supporting architecture and build documents | `docs/architecture/` |
| Runtime stack | Local demo orchestration for API, simulator, frontend, Kafka, TimescaleDB, Redis, and Zookeeper | `docker-compose.yml` |

## Quick Start

Docker Compose is the recommended way to run the local demo stack.

```bash
docker-compose up --build
```

Verified services from `docker-compose.yml`:

| Service | Purpose | Port |
| --- | --- | --- |
| `frontend` | React dashboard served by nginx | `3000` |
| `api` | FastAPI backend and WebSocket stream | `8000` |
| `kafka` | Kafka broker | `9092`, `29092` |
| `zookeeper` | Kafka coordination | `2181` |
| `timescaledb` | PostgreSQL/TimescaleDB storage | `5432` |
| `redis` | Latest-state cache | `6379` |
| `simulator` | Synthetic sensor publisher | internal only |

After startup:

- API docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`
- Dashboard: `http://localhost:3000`
- WebSocket stream: `ws://localhost:8000/twin/stream`

## Local Development

Backend setup:

```bash
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Sensor simulator:

```bash
cd sensor_simulator
python kafka_publisher.py --demo
```

React dashboard:

```bash
cd frontend/react-dashboard
npm install
npm start
```

For local environment variables, copy `.env.example` to `.env` and provide only the credentials or endpoints needed for your local test. Do not commit secrets.

## Demo Scenarios

These scenarios are simulated examples for demonstrating system behavior. They are not verified production outcomes.

1. **Failure prediction demo:** WP-07 / `GDC-WP-007` is used as the main synthetic demo asset, with a 34% example failure probability in the baseline 30-day story.
2. **What-if maintenance deferral:** Deferring maintenance by 45 days is represented as a simulated increase from 34% to 68% failure probability in the calibrated demo route.
3. **Expected-cost illustration:** A USD 180,000 unplanned failure at 68% risk gives a USD 122,400 simulated expected failure cost, compared with an USD 8,000 inspection-cost assumption.
4. **Maintenance scheduling concept:** Scheduler code supports a 90-day maintenance planning story and priority work-order output for demo use.
5. **Visualization workflow:** React and Unity clients consume API/WebSocket data to present synthetic asset state and risk context.

## API Endpoints

Representative verified routes from `api/main.py` and `api/routers/`:

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | API health check |
| `GET` | `/ready` | Readiness check for Redis, TimescaleDB, and Kafka availability |
| `GET` | `/status` | Demo/system status |
| `GET` | `/disclaimer` | Synthetic-data disclaimer payload |
| `WS` | `/twin/stream` | Real-time synthetic asset stream for dashboard and visualization clients |
| `GET` | `/api/assets` | Synthetic asset list |
| `GET` | `/api/assets/{asset_id}` | Single synthetic asset record |
| `GET` | `/api/assets/class/{asset_class}` | Assets filtered by class |
| `GET` | `/api/twins/{asset_id}/sensors/latest` | Latest twin sensor payload for an asset |
| `GET` | `/api/twins/{asset_id}/sensors/history` | Twin sensor history payload |
| `GET` | `/api/sensors/{asset_id}/latest` | Latest synthetic sensor readings |
| `GET` | `/api/sensors/{asset_id}/history` | Historical synthetic sensor readings |
| `GET` | `/api/sensors/{asset_id}/summary` | Sensor summary statistics |
| `POST` | `/api/monte-carlo/simulate` | Monte Carlo failure-risk simulation |
| `POST` | `/api/monte-carlo/whatif` | Calibrated demo what-if route accepting `deferral_days` or `maintenance_date` |
| `GET` | `/api/monte-carlo/health-check` | Monte Carlo engine health check |
| `POST` | `/whatif/simulate` | What-if simulation by maintenance date |
| `POST` | `/whatif/simulate-days` | What-if simulation by deferral days |
| `GET` | `/whatif/alerts` | Active demo alerts |
| `POST` | `/api/predict/failure` | LSTM failure-prediction API with fallback behavior |
| `GET` | `/api/predict/failure/{asset_id}` | Demo prediction for an asset |
| `GET` | `/api/predict/model/info` | Prediction model and artifact status |
| `GET` | `/api/anomaly/status` | Synthetic anomaly scores for known assets |
| `GET` | `/api/anomaly/status/{asset_id}` | Synthetic anomaly score for one asset |
| `POST` | `/api/anomaly/batch` | Batch anomaly scoring |
| `GET` | `/api/anomaly/model/info` | Anomaly model status |
| `GET` | `/maximo/assets` | Mock/demo Maximo asset list |
| `GET` | `/maximo/assets/{asset_id}` | Mock/demo Maximo asset record |
| `GET` | `/maximo/alerts` | Mock/demo active alerts |
| `POST` | `/maximo/workorder` | Mock/demo work-order creation |
| `POST` | `/api/watsonx/whatif-nlp` | Natural-language what-if adapter |
| `GET` | `/api/watsonx/health` | watsonx adapter health |
| `POST` | `/api/watsonx/extract` | Parameter extraction test endpoint |
| `GET` | `/api/watsonx/examples` | Example what-if prompts |
| `POST` | `/api/agent/trigger` | Supporting cross-agent trigger endpoint |
| `GET` | `/api/agent/health` | Agent integration health |
| `POST` | `/api/agent/test-trigger` | Demo trigger event |

## Technology Stack

| Area | Technologies |
| --- | --- |
| Backend/API | Python, FastAPI, Uvicorn, Pydantic |
| Data pipeline | Kafka, Zookeeper, synthetic sensor publisher |
| Storage/cache | TimescaleDB/PostgreSQL, Redis |
| AI/ML/simulation | NumPy, SciPy, scikit-learn, Monte Carlo simulation, LSTM/CNN model areas, synthetic fallbacks |
| Frontend/visualization | React, Recharts, nginx, Unity, Three.js project area |
| IBM/Red Hat alignment | Maximo adapter layer, watsonx.ai adapter, Watson IoT/OpenShift environment placeholders, Kafka/Event Streams alignment concepts |

## Demo Context

This repository demonstrates an industrial digital twin concept for geothermal asset monitoring and predictive maintenance. The implementation uses synthetic sensor data and simulated failure scenarios. It is inspired by operational technology environments, but does not include live plant data, private client data, production credentials, or confidential operational records.

## Demo Assumptions

ROI, risk, failure probability, and expected-cost examples in this repository are demonstration assumptions and simulation outputs. They should not be treated as verified production financial results, validated plant reliability metrics, or evidence of deployed operational performance.

The baseline demo narrative includes a 34% to 68% maintenance-deferral example and a USD 122,400 expected-cost illustration. These values are useful for explaining the demo flow, but they are not field measurements.

## Security & Privacy Notes

- Synthetic data is used for demo flows.
- `.env.example` is a template only.
- Do not commit secrets, tokens, credentials, private URLs, or production `.env` files.
- No live operational data is required or included for the local demo.
- Review all datasets and exported artifacts before sharing outside a controlled context.
- Treat integration credentials as environment variables only.
- IBM, Maximo, watsonx.ai, OpenShift, and other integration credentials must remain outside source control.

## Limitations

- Demonstration prototype, not a production system.
- Synthetic data and simulated scenarios only.
- Some integrations are mocked, paused, or represented as adapter layers.
- ML model paths include fallback behavior; operational model validation is still required before real deployment.
- CNN anomaly scoring is synthetic unless a trained model artifact is present and preprocessing is fully wired.
- Real Maximo, Watson IoT, watsonx.ai, Watson Studio, OpenShift, and production cloud execution are not claimed here.
- Operational use would require security review, integration testing, model validation, observability, reliability engineering, and domain expert approval.

## Roadmap

- Harden API authentication and authorization
- Add production-grade observability and structured logging
- Add a model validation and release pipeline
- Improve deployment and OpenShift documentation
- Add screenshots and a short demo video
- Add a polished architecture diagram
- Add or expand tests and CI where gaps remain
- Improve data schema and sensor-contract documentation
- Document mocked versus live integration modes more explicitly

## Status

| Area | Status |
| --- | --- |
| Current status | Demonstration prototype |
| Data | Synthetic / simulated |
| Deployment target | Local Docker Compose demo, with cloud/OpenShift concepts documented where applicable |
| Production readiness | Not production-ready |

## License

MIT - see `LICENSE`.
