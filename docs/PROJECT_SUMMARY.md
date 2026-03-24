# OT DIGITAL TWIN - PROJECT SUMMARY

**Last Updated**: March 23, 2026  
**Status**: Planning Phase Complete  
**Days to Demo**: 7 days (March 30-31, 2026)

---

## 📊 PROJECT STATUS

### Current Phase
✅ **Phase 0**: Project Review & Understanding - COMPLETE  
🔄 **Phase 1**: Foundation & Environment Setup - IN PROGRESS  
⏳ **Phase 2-7**: Implementation phases - PENDING

### Team Readiness
- **Technical Lead** (Wisdom Kinoti): Ready to coordinate
- **Sensor Lead** (Philip Mukiti): Awaiting Phase 2 kickoff
- **ML Lead** (Asenath Wairimu): Awaiting Phase 3 kickoff
- **XR Lead** (Maurine Muthoni): Awaiting Phase 6 kickoff

---

## 🎯 WHAT WE'RE BUILDING

### The Problem
Geothermal power plants experience unexpected equipment failures causing:
- $8.2M in downtime costs per incident
- Safety risks to personnel
- Lost revenue from power generation
- Reactive "fix when broken" maintenance approach

### Our Solution
AI-powered predictive maintenance system that:
- Predicts bearing failures 7-14 days in advance
- Prevents downtime with $150K preventive maintenance (54x ROI)
- Provides real-time 3D visualization of plant status
- Automates work order creation in IBM Maximo
- Enables "what-if" scenario planning

### Target Customer
**GDC Kenya** (Geothermal Development Company)
- 5 geothermal power plants
- 863 MW total capacity
- 51% of Kenya's renewable energy
- Demo scheduled: March 30-31, 2026

---

## 🏗️ SYSTEM ARCHITECTURE

### High-Level Flow
```
┌─────────────────┐
│ Sensor Simulator│ (Philip)
│  6 Sensors      │
│  OPC-UA         │
└────────┬────────┘
         │ MQTT
         ▼
┌─────────────────┐
│ Watson IoT      │ (IBM Cloud)
│ Platform        │
└────────┬────────┘
         │ Kafka
         ▼
┌─────────────────┐
│ FastAPI Backend │ (Wisdom)
│ • Anomaly AI    │
│ • Monte Carlo   │ (Asenath)
│ • Maximo API    │
└────────┬────────┘
         │ WebSocket
         ▼
┌─────────────────────────────┐
│  Frontend (Maurine)         │
│  • React Dashboard          │
│  • Unity 3D Twin            │
└─────────────────────────────┘
```

### The 5 AI Agents

1. **Failure Predictor** (LSTM Neural Network)
   - Learns temporal patterns in sensor data
   - Trained on 1 year of synthetic failure events
   - Predicts failure probability 7-14 days ahead
   - Technology: TensorFlow/Keras

2. **Monte Carlo Engine**
   - Runs 10,000 probabilistic scenarios
   - Accounts for sensor measurement uncertainty
   - Quantifies failure risk as percentage
   - Technology: scipy.stats, numpy

3. **Maintenance Scheduler**
   - Finds optimal maintenance window
   - Balances risk vs. operational needs
   - Considers production schedules
   - Technology: Custom optimization algorithm

4. **Anomaly AI**
   - Real-time sensor classification
   - Categories: NORMAL / WARNING / CRITICAL
   - Phase 1: Threshold-based (fast)
   - Phase 2: CNN model (sophisticated)

5. **What-If Analyst**
   - Interactive scenario simulation
   - "What if we delay maintenance 5 days?"
   - Recalculates failure probability
   - Enables data-driven decision making

---

## 🔧 TECHNOLOGY STACK

### Backend
- **Language**: Python 3.11
- **API Framework**: FastAPI (async, high-performance)
- **Message Queue**: Apache Kafka 3.6
- **Time-Series DB**: TimescaleDB (PostgreSQL extension)
- **Cache**: Redis 7
- **ML Libraries**: TensorFlow, scikit-learn, scipy, numpy, pandas

### Frontend
- **Web Dashboard**: React 18 + TypeScript
- **3D Visualization**: Unity 2022.3 LTS
- **Charts**: Recharts
- **WebSocket**: Native WebSocket API

### IBM Cloud Services
- **Watson IoT Platform**: Device management, MQTT broker
- **IBM Maximo MAS 9.1**: Work order management
- **watsonx.ai**: LSTM model training
- **Red Hat OpenShift 4.14**: Container orchestration

### DevOps
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions
- **Containers**: Docker + Docker Compose
- **Orchestration**: Kubernetes (OpenShift)

---

## 📅 7-DAY BUILD PLAN

### Day 1 (March 23 - TODAY)
**Foundation & Environment Setup**
- [x] Project review and understanding
- [ ] GitHub repository setup
- [ ] Local development environment (Docker, Python, Node.js)
- [ ] IBM TechZone provisioning
- [ ] Environment variables configuration

**Deliverables**:
- GitHub repo with proper structure
- docker-compose.yml running locally
- .env file configured
- CI/CD pipeline active

### Day 2 (March 24)
**Sensor Simulator + Watson IoT**
- [ ] Build synthetic sensor data generator
- [ ] Implement OPC-UA simulator
- [ ] Connect to Watson IoT via MQTT
- [ ] Test end-to-end data flow

**Deliverables**:
- `sensor_simulator/` module complete
- Data flowing to Watson IoT
- Anomaly injection working

### Day 3 (March 25)
**Monte Carlo Engine + Data Pipeline**
- [ ] Generate synthetic training data
- [ ] Implement Monte Carlo simulation
- [ ] Create LSTM model architecture
- [ ] Set up Kafka consumer

**Deliverables**:
- `monte_carlo/` module complete
- 10,000-iteration simulation working
- Training data generated

### Day 4 (March 26)
**FastAPI Backend + Integration**
- [ ] Build FastAPI application
- [ ] Implement Anomaly AI
- [ ] Connect databases (TimescaleDB, Redis)
- [ ] Integrate Monte Carlo engine
- [ ] Set up WebSocket streaming

**Deliverables**:
- `api/` module complete
- All endpoints functional
- WebSocket broadcasting working

### Day 5 (March 27)
**React Dashboard**
- [ ] Build React application
- [ ] Create sensor gauge components
- [ ] Implement failure probability display
- [ ] Add What-If Analyst slider
- [ ] Work order panel

**Deliverables**:
- `frontend/react-dashboard/` complete
- Real-time updates working
- What-If slider functional

### Day 6 (March 28)
**Unity XR Visualization**
- [ ] Set up Unity project
- [ ] Implement WebSocket SensorBridge
- [ ] Create 3D asset color binding
- [ ] Build HUD with probability gauge
- [ ] Test real-time updates

**Deliverables**:
- `frontend/unity-twin/` complete
- 3D twin responding to sensor data
- Color changes working (green → yellow → red)

### Day 7 (March 29)
**Integration Testing & Rehearsal**
- [ ] End-to-end pipeline testing
- [ ] Demo script rehearsal (3x)
- [ ] Backup video recording
- [ ] Contingency plan validation
- [ ] Final sign-off

**Deliverables**:
- All components integrated
- Demo rehearsed and polished
- Backup plans ready
- Team confident

---

## 📋 KEY TECHNICAL CONCEPTS

### 1. OPC-UA (Open Platform Communications - Unified Architecture)
**What**: Industrial communication protocol for sensors and PLCs  
**Why**: Industry standard for manufacturing and energy sectors  
**How**: We simulate it with Python opcua library  
**In Our Project**: Generates synthetic geothermal sensor data

### 2. MQTT (Message Queuing Telemetry Transport)
**What**: Lightweight pub/sub messaging protocol  
**Why**: Designed for IoT devices with limited bandwidth  
**How**: Watson IoT Platform acts as MQTT broker  
**In Our Project**: Transports sensor data from simulator to cloud

### 3. Apache Kafka
**What**: Distributed event streaming platform  
**Why**: Handles millions of messages per second  
**How**: Decouples data producers from consumers  
**In Our Project**: Buffers sensor data between Watson IoT and FastAPI

### 4. Monte Carlo Simulation
**What**: Statistical method using random sampling  
**Why**: Quantifies uncertainty in predictions  
**How**: Run 10,000 scenarios with slightly different sensor values  
**In Our Project**: Calculates failure probability (e.g., 34% chance)

### 5. LSTM (Long Short-Term Memory)
**What**: Type of recurrent neural network  
**Why**: Excellent at learning time-series patterns  
**How**: Trained on historical sensor data with failure labels  
**In Our Project**: Predicts bearing failures 7-14 days ahead

### 6. TimescaleDB
**What**: PostgreSQL extension for time-series data  
**Why**: 10-100x faster than regular PostgreSQL for time queries  
**How**: Automatically partitions data by time (hypertables)  
**In Our Project**: Stores millions of sensor readings efficiently

### 7. WebSocket
**What**: Full-duplex communication protocol  
**Why**: Real-time bidirectional data flow  
**How**: Persistent connection between server and clients  
**In Our Project**: Broadcasts sensor updates to React and Unity

### 8. IEEE ZAHIRA 2025 (7-Layer IoT Architecture)
**What**: Standard for industrial IoT systems  
**Why**: Ensures interoperability and scalability  
**Layers**:
- L1: Device (sensors, actuators)
- L2: Edge (local processing)
- L3: Network (communication)
- L4: Platform (data management)
- L5: Analytics (AI/ML)
- L6: Application (user interfaces)
- L7: Business (integration with ERP/MES)

**In Our Project**: We implement all 7 layers

---

## 🎬 DEMO SCRIPT (5 Minutes)

### T-30 Minutes: Pre-Demo Checklist
- [ ] All services running and healthy
- [ ] WebSocket connections stable
- [ ] Sensors updating every 1 second
- [ ] Anomaly injector ready
- [ ] Backup video loaded on laptop
- [ ] Presenter notes printed
- [ ] Water bottles for presenters

### 0:00 - Introduction (45 seconds)
**Wisdom**: "Good morning. I'm Wisdom Kinoti, Technical Lead at i3 Technologies. Today we're demonstrating an AI-powered predictive maintenance system for GDC Kenya's geothermal power plants. This system predicts equipment failures 7-14 days in advance, preventing $8.2M in downtime with just $150K in preventive maintenance."

**Show**: React dashboard with normal operation (all green)

### 0:45 - Trigger Anomaly (30 seconds)
**Philip**: "Let me simulate a bearing degradation event that we've observed in real plants."

**Action**: Press anomaly injection button

**Show**: 
- Bearing vibration spikes from 4.2 → 9.5 mm/s
- Temperature rises from 83°C → 108°C
- Status changes: GREEN → YELLOW → RED

### 1:15 - Show Detection (20 seconds)
**Wisdom**: "Our Anomaly AI detected this in under 1 second and classified it as CRITICAL."

**Show**: 
- Anomaly score: 0.98
- Status banner turns red
- Alert notification appears

### 1:35 - Show Monte Carlo Result (30 seconds)
**Asenath**: "The system automatically ran 10,000 Monte Carlo simulations to quantify the failure risk."

**Show**:
- Failure probability: 34%
- Days to failure: 12 days (P50)
- Recommended action: SCHEDULE_MAINTENANCE
- Optimal date: April 4, 2026

### 2:05 - Show Work Order (30 seconds)
**Wisdom**: "Because the probability exceeded our 25% threshold, the system automatically created a work order in IBM Maximo."

**Show**:
- Work order ID: WO-2026-0324-001
- Asset: GDC-TURBINE-01
- Priority: High
- Scheduled date: April 4, 2026
- Estimated cost: $150K

### 2:35 - What-If Slider Demo (50 seconds)
**Asenath**: "Let's use the What-If Analyst to see what happens if we delay maintenance."

**Action**: Move slider to April 10 (+6 days)

**Show**:
- Probability increases: 34% → 67%
- Action changes: SCHEDULE → URGENT
- Cost impact: $150K → $8.2M (if failure occurs)

**Asenath**: "This shows the financial impact of delaying maintenance. The data clearly supports acting on April 4th."

### 3:25 - Unity 3D Twin (40 seconds)
**Maurine**: "For immersive visualization, we've created a 3D digital twin in Unity."

**Show**:
- 3D model of turbine
- Color changes in real-time (red)
- HUD showing failure probability
- Camera fly-through

**Maurine**: "Operators can use VR headsets to inspect the plant remotely and see real-time status."

### 4:05 - Business Value (40 seconds)
**Wisdom**: "Let me summarize the business value:
- **Prevention**: Avoid $8.2M downtime with $150K maintenance
- **ROI**: 54x return on investment
- **Safety**: Prevent catastrophic failures
- **Efficiency**: Optimize maintenance schedules
- **Scalability**: Deploy across all 5 GDC plants"

### 4:45 - Closing (15 seconds)
**Wisdom**: "Thank you. We're ready to deploy this system at GDC Kenya. Questions?"

---

## 🚨 CONTINGENCY PLANS

### Plan A: Live Demo (Primary)
- All systems running in real-time
- Anomaly injection on command
- Interactive What-If slider

### Plan B: Pre-Recorded Demo (If WebSocket fails)
- 5-minute video showing full workflow
- Narrated by team
- Includes all key moments

### Plan C: Offline Mode (If internet fails)
- Local docker-compose stack
- CSV replay instead of Watson IoT
- React dashboard only (no Unity)

### Plan D: Slide Deck (If total failure)
- Screenshots of working system
- Architecture diagrams
- Business case slides
- Video clips embedded

---

## 📊 SUCCESS METRICS

### Technical Metrics
- [ ] End-to-end latency < 3 seconds
- [ ] WebSocket uptime > 99% during demo
- [ ] Monte Carlo execution < 2 seconds
- [ ] Zero crashes during 3 rehearsals
- [ ] All 5 AI agents functional

### Demo Metrics
- [ ] Smooth transitions between presenters
- [ ] Anomaly visible within 1 second
- [ ] Work order creation automatic
- [ ] What-If slider responsive
- [ ] Unity 3D twin synchronized

### Business Metrics
- [ ] Letter of Intent from GDC Kenya
- [ ] 3+ qualified leads from attendees
- [ ] Media coverage (1+ article)
- [ ] Team confidence: 9/10 or higher
- [ ] Positive feedback from IBM executives

---

## 🎓 LEARNING APPROACH

### "No Vibe Coding" Philosophy
You requested: **"not vibe coding, i want to understand what am doing"**

Our approach:
1. **Explain WHY before HOW**: Every technical decision is justified
2. **Step-by-step documentation**: No magic, no shortcuts
3. **Conceptual understanding**: Learn the principles, not just syntax
4. **Professional practices**: GitHub workflow, testing, CI/CD
5. **Hands-on building**: You write the code, I guide

### Documentation Standards
- **Code comments**: Explain WHY, not WHAT
- **Commit messages**: Clear, specific, actionable
- **README files**: Purpose, usage, troubleshooting
- **Architecture docs**: System design, data flow, decisions

---

## 📞 TEAM CONTACTS

- **Technical Lead**: Wisdom Kinoti (you)
- **Sensor Lead**: Philip Mukiti
- **ML Lead**: Asenath Wairimu
- **XR Lead**: Maurine Muthoni
- **Organization**: i3 Technologies (CEID 7sq30)
- **Location**: IBM Research Lab Africa, CUEA
- **Demo Date**: March 30-31, 2026

---

## 🎯 IMMEDIATE NEXT STEPS

### Today (March 23)
1. ✅ Review this summary document
2. [ ] Set up GitHub repository (PHASE_1_FOUNDATION.md)
3. [ ] Install prerequisites (Python, Node.js, Docker)
4. [ ] Start docker-compose stack
5. [ ] Reserve IBM TechZone environments
6. [ ] Create .env file

### Tomorrow (March 24)
1. [ ] Build sensor simulator (PHASE_2_SENSOR_SIMULATOR.md)
2. [ ] Test Watson IoT connection
3. [ ] Verify data flow to Kafka

### This Week
- Follow the 7-day build plan
- Document everything
- Test thoroughly
- Ask questions when unclear

---

## ❓ QUESTIONS TO CONSIDER

Before starting implementation, think about:

1. **Team Coordination**: How will Philip, Asenath, and Maurine collaborate?
2. **Git Workflow**: Who reviews pull requests? Who merges to main?
3. **Testing Strategy**: Unit tests? Integration tests? Manual testing?
4. **Demo Rehearsal**: When? How many times? Who presents what?
5. **Backup Plans**: What if Watson IoT is down? What if Unity crashes?
6. **Post-Demo**: What happens after March 31? Deployment? Handoff?

---

**Ready to start building? Let's begin with Phase 1! 🚀**