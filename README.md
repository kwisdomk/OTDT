# OT Digital Twin — Build Guide v1.0 Implementation

> **Source of truth:** `docs/Build_Guide_v1.0.pdf`  
> **Started:** 28 March 2026  
> **Root:** `Q:\bcs\ibm\EAAAIW @ IBM Research Lab Africa\OTDT\otdt\OTDT`

> ⚠️ **SYNTHETIC DATA:** All sensor readings are computer-generated. Not representative of any real client operational data.

---

## Build Guide Steps

| # | Step | Status | Owner |
|---|------|--------|-------|
| 1 | TechZone Provisioning | ⬜ Not Started | Wisdom |
| 2 | Maximo Monitor Data Load | ⬜ Not Started | Wisdom |
| 3 | Unity XR 3D Model | ⬜ Not Started | Maurine |
| 4 | LSTM Training (Watson Studio) | ⬜ Not Started | Asenath |
| 5 | Monte Carlo with Weibull | ⚠️ Partial | Asenath |
| 6 | What-If in Unity | ⬜ Not Started | Maurine |
| 7 | CNN Anomaly AI | ⬜ Not Started | Asenath |
| 8 | Maintenance Scheduler | ⬜ Not Started | Asenath |
| 9 | OpenShift Deployment | ⬜ Not Started | Wisdom |

Full detail: [BUILD_GUIDE_STATUS.md](BUILD_GUIDE_STATUS.md)

---

## Repository Structure

```
OTDT/
├── api/                    # FastAPI + WebSocket (existing ✅)
├── monte_carlo/            # Monte Carlo engine (existing ✅)
├── sensor_simulator/       # Synthetic data generator (existing ✅)
├── frontend/               # React dashboard (existing ✅, secondary)
├── maximo/                 # Step 2: Maximo MAS 9.1 integration
├── unity/                  # Step 3 & 6: Unity XR 3D model
├── ml/                     # Steps 4 & 7: LSTM + CNN
│   ├── lstm/
│   └── cnn_anomaly/
├── scheduler/              # Step 8: Maintenance optimizer
├── deployment/             # Step 9: OpenShift manifests
│   └── openshift/
│       ├── base/
│       └── overlays/{dev,prod}/
├── datasets/               # GDC_Assets.xlsx, Sensor_Readings.xlsx
├── infrastructure/         # Step 1: TechZone / Terraform
├── scripts/                # Utility scripts (this script)
└── docs/                   # Architecture, API reference
```

---

## Quick Start (local / synthetic data only)

```bash
cp .env.example .env        # fill TechZone credentials
docker-compose up           # starts API + simulator
# React dashboard: http://localhost:3000
# WebSocket:       ws://localhost:8000/twin/stream
# API docs:        http://localhost:8000/docs
```

---

## Team

| Role | Owner | Steps |
|------|-------|-------|
| Infrastructure + API + Deployment | Wisdom Kinoti | 1, 2, 9 |
| Unity XR + Frontend | Maurine Chebet | 3, 6 |
| ML + Monte Carlo + Scheduler | Asenath Atieno Rachael | 4, 5, 7, 8 |

---

## License
i3 Technologies Ltd — Confidential  
IBM & Red Hat Silver Partner | CEID: 7sq30
