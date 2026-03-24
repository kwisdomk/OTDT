# OT DIGITAL TWIN - COMPREHENSIVE BUILD PLAN

**Project**: Industrial Predictive Maintenance System for Geothermal Power Plants  
**Timeline**: March 23-31, 2026 (7 days to demo)  
**Approach**: Step-by-step, fully documented, professional GitHub workflow

---

## 🎯 PROJECT OVERVIEW

### What We're Building
A real-time AI-powered system that predicts equipment failures in geothermal power plants 7-14 days before they happen, preventing $8.2M in downtime with $150K preventive maintenance.

### System Architecture
```
Synthetic Sensors → OPC-UA → Watson IoT → Kafka → 
FastAPI (Anomaly AI + Monte Carlo) → WebSocket → 
React Dashboard + Unity 3D Twin
```

### The 5 AI Agents
1. **Failure Predictor** (LSTM): Learns temporal failure patterns
2. **Monte Carlo Engine**: Runs 10,000 probabilistic scenarios
3. **Maintenance Scheduler**: Finds optimal maintenance window
4. **Anomaly AI**: Classifies sensor readings (NORMAL/WARNING/CRITICAL)
5. **What-If Analyst**: Simulates different maintenance dates

---

## 📅 7-DAY BUILD SCHEDULE

### Day 1 (March 23 - TODAY)
**Focus**: Foundation & Environment Setup
- ✅ Project review and understanding
- 🔄 GitHub repository setup with professional structure
- 🔄 Development environment configuration
- 🔄 IBM TechZone environment provisioning

### Day 2 (March 24)
**Focus**: Sensor Simulator + Watson IoT
- Build synthetic sensor data generator
- Implement OPC-UA simulator
- Connect to Watson IoT Platform via MQTT
- Test end-to-end sensor data flow

### Day 3 (March 25)
**Focus**: Monte Carlo Engine + Data Pipeline
- Build synthetic training data generator
- Implement Monte Carlo simulation engine
- Create LSTM model architecture
- Set up Kafka consumer pipeline

### Day 4 (March 26)
**Focus**: FastAPI Backend + Integration
- Build FastAPI application structure
- Implement Anomaly AI detector
- Connect to TimescaleDB and Redis
- Integrate Monte Carlo engine
- Set up WebSocket streaming

### Day 5 (March 27)
**Focus**: React Dashboard
- Build React application with WebSocket
- Create sensor gauge components
- Implement failure probability display
- Add What-If Analyst slider
- Work order panel integration

### Day 6 (March 28)
**Focus**: Unity XR Visualization
- Set up Unity project and scene
- Implement WebSocket SensorBridge
- Create 3D asset color binding
- Build HUD with probability gauge
- Test real-time updates

### Day 7 (March 29)
**Focus**: Integration Testing & Rehearsal
- End-to-end pipeline testing
- Demo script rehearsal (3x)
- Backup video recording
- Contingency plan validation
- Final sign-off

---

## 📚 DETAILED GUIDES

This build plan is organized into focused guides for each phase:

1. **[PHASE_1_FOUNDATION.md](PHASE_1_FOUNDATION.md)** - GitHub setup, dev environment, IBM TechZone
2. **[PHASE_2_SENSOR_SIMULATOR.md](PHASE_2_SENSOR_SIMULATOR.md)** - Synthetic sensors, OPC-UA, Watson IoT
3. **[PHASE_3_MONTE_CARLO.md](PHASE_3_MONTE_CARLO.md)** - Monte Carlo engine, LSTM model, data generation
4. **[PHASE_4_FASTAPI_BACKEND.md](PHASE_4_FASTAPI_BACKEND.md)** - FastAPI, Kafka, TimescaleDB, WebSocket
5. **[PHASE_5_REACT_DASHBOARD.md](PHASE_5_REACT_DASHBOARD.md)** - React frontend, WebSocket client, What-If slider
6. **[PHASE_6_UNITY_XR.md](PHASE_6_UNITY_XR.md)** - Unity 3D twin, WebSocket bridge, real-time updates
7. **[PHASE_7_INTEGRATION.md](PHASE_7_INTEGRATION.md)** - End-to-end testing, demo rehearsal, deployment

---

## 🏗️ REPOSITORY STRUCTURE

```
OTDT/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD
├── docs/
│   ├── architecture.md            # System architecture
│   ├── api-documentation.md       # API endpoints
│   └── deployment-guide.md        # Deployment instructions
├── sensor_simulator/
│   ├── __init__.py
│   ├── simulator.py               # OPC-UA sensor generator
│   ├── watson_iot_publisher.py    # MQTT publisher
│   ├── anomaly_injector.py        # Demo anomaly trigger
│   ├── config.py                  # Configuration
│   └── requirements.txt
├── monte_carlo/
│   ├── __init__.py
│   ├── engine.py                  # Monte Carlo simulation
│   ├── lstm_model.py              # LSTM failure predictor
│   ├── scheduler.py               # Maintenance scheduler
│   ├── data_generator.py          # Synthetic training data
│   └── requirements.txt
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── routers/
│   │   ├── sensors.py
│   │   ├── twin.py
│   │   ├── monte_carlo.py
│   │   ├── maximo.py
│   │   └── whatif.py
│   ├── anomaly/
│   │   └── detector.py            # Anomaly AI
│   ├── integrations/
│   │   ├── kafka_consumer.py
│   │   ├── maximo_client.py
│   │   └── watson_iot.py
│   ├── db/
│   │   ├── timescale.py
│   │   └── redis_client.py
│   ├── middleware/
│   │   └── system_control.py      # Kill switch
│   └── requirements.txt
├── frontend/
│   ├── react-dashboard/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── App.jsx
│   │   └── package.json
│   └── unity-twin/
│       ├── Assets/
│       │   ├── Scripts/
│       │   ├── Scenes/
│       │   └── Materials/
│       └── ProjectSettings/
├── k8s/
│   ├── kafka.yaml
│   ├── api-deployment.yaml
│   ├── frontend-deployment.yaml
│   └── redis-deployment.yaml
├── .env.example                   # Environment template
├── .gitignore
├── docker-compose.yml             # Local development
├── requirements.txt               # Root dependencies
├── README.md
└── BUILD_PLAN.md                  # This file
```

---

## 🔄 GIT WORKFLOW

### Branching Strategy
- `main` - Production-ready code (frozen until demo)
- `dev` - Integration branch
- `feature/sensor-simulator` - Philip's work
- `feature/monte-carlo` - Asenath's work
- `feature/api` - Wisdom's work
- `feature/frontend` - Maurine's work

### Commit Convention
```
<type>/<scope>: <description>

Types: feat, fix, test, docs, refactor, ci, deploy, chore
Scopes: sensor, mc, api, frontend, unity, db, k8s, ci

Examples:
feat/sensor: add opcua geothermal turbine simulator 6-sensor synthetic data
feat/mc: implement monte carlo engine 10k iterations scipy stats
feat/api: add websocket twin stream 5s asset state broadcast
```

---

## 📊 SUCCESS METRICS

### Technical
- [ ] All 3 components working together
- [ ] End-to-end latency <3 seconds
- [ ] WebSocket stable for 15+ minutes
- [ ] Monte Carlo accuracy >85%
- [ ] Zero crashes during 3 rehearsals

### Demo
- [ ] Smooth presenter transitions
- [ ] Anomaly detection visible in <1 second
- [ ] Work order creation automatic
- [ ] What-If slider responsive
- [ ] Delegates understand value prop

### Business
- [ ] Letter of Intent from GDC Kenya
- [ ] 3+ qualified leads
- [ ] Media coverage
- [ ] Team confidence high

---

## 🚨 RISK MITIGATION

### Critical Risks

1. **Watson IoT Connection Fails**
   - Mitigation: Pre-recorded CSV replay mode
   - Test: Verify connection 24 hours before demo

2. **Monte Carlo Too Slow**
   - Mitigation: Reduce iterations to 5000
   - Test: Measure latency, must be <3 seconds

3. **WebSocket Drops During Demo**
   - Mitigation: Auto-reconnect in 2 seconds
   - Test: Kill connection, verify reconnect

4. **Unity Crashes**
   - Mitigation: React dashboard shows same data
   - Test: Full demo with Unity closed

5. **Total System Failure**
   - Mitigation: Pre-recorded backup video
   - Test: Video plays smoothly on demo laptop

---

## 🎯 GETTING STARTED

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Unity 2022.3 LTS
- Git
- VS Code (recommended)

### Quick Start
```bash
# 1. Clone repository
git clone <repo-url>
cd OTDT

# 2. Set up environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start local stack
docker-compose up -d

# 4. Follow phase guides in order
# Start with PHASE_1_FOUNDATION.md
```

---

## 📞 SUPPORT

- **Technical Lead**: Wisdom Kinoti
- **Sensor Lead**: Philip Mukiti
- **ML Lead**: Asenath Wairimu
- **XR Lead**: Maurine Muthoni
- **Demo Date**: March 30-31, 2026
- **Location**: IBM Research Lab Africa, CUEA

---

## 🎓 LEARNING OBJECTIVES

By the end of this build, you will understand:
- Industrial IoT protocols (OPC-UA, MQTT)
- Monte Carlo simulation for risk analysis
- Real-time data streaming with Kafka
- WebSocket communication patterns
- Time-series database optimization
- React state management with WebSocket
- Unity 3D real-time data binding
- Professional Git workflow
- CI/CD with GitHub Actions
- IBM Cloud platform integration

---

## 📝 NEXT STEPS

**Ready to start building?**

1. Read [PHASE_1_FOUNDATION.md](PHASE_1_FOUNDATION.md) for GitHub setup
2. Follow each phase guide sequentially
3. Document your progress in this file
4. Ask questions when concepts are unclear
5. Test thoroughly at each step

**Let's build something amazing! 🚀**