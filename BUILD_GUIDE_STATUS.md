# OT Digital Twin — Build Guide v1.0 Status Tracker
> **Source of truth:** `docs/Build_Guide_v1.0.pdf`  
> **Last updated:** 28 March 2026  
> **Overall progress:** ▓▓░░░░░░░░░░░░░░ 2/9 steps complete (~22%)

---

## Step Progress

| # | Step | Status | Owner | Evidence Required |
|---|------|--------|-------|-------------------|
| 1 | TechZone Provisioning | ⬜ Not Started | Wisdom | OCP URL, Maximo URL, Watson Studio URL, TechZone reservation IDs |
| 2 | Maximo Monitor Data Load | ⬜ Not Started | Wisdom | Asset hierarchy loaded (50 assets), sensor data points configured, REST API responding |
| 3 | Unity XR 3D Model | ⬜ Not Started | Maurine | `.glb` imported, scene hierarchy matches asset list, colour controller working |
| 4 | LSTM Training (Watson Studio) | ⬜ Not Started | Asenath | AUC-ROC > 0.82, training notebook committed, `.h5` model exported to COS |
| 5 | Monte Carlo with Weibull | ⚠️ Partial | Asenath | Normal → Weibull distributions, sensor covariates integrated, 10k runs < 5s |
| 6 | What-If in Unity | ⬜ Not Started | Maurine | Unity slider UI connected to `/whatif/simulate`, response < 2s, colour update visible |
| 7 | CNN Anomaly AI | ⬜ Not Started | Asenath | >80% accuracy, training notebook committed, Unity polling endpoint live |
| 8 | Maintenance Scheduler | ⬜ Not Started | Asenath | Gantt chart rendered, Maximo WO creation working, LP constraints validated |
| 9 | OpenShift Deployment | ⬜ Not Started | Wisdom | Public OCP Route URL, all pods Running, health checks passing |

---

## Evidence Checklist

### Step 1 — TechZone Provisioning
- [ ] Maximo MAS 9.1 environment reserved and active
- [ ] Watson Studio ML Lab provisioned
- [ ] Red Hat OpenShift 4.14 cluster active
- [ ] All URLs documented in `.env`

### Step 2 — Maximo Monitor Data Load
- [ ] `datasets/GDC_Assets.xlsx` created (50 assets, all columns)
- [ ] `maximo/asset_loader.py` implemented and tested
- [ ] Asset hierarchy visible in Maximo UI
- [ ] `maximo/monitor_client.py` returning live sensor data
- [ ] `/api/assets` endpoint returning Maximo data

### Step 3 — Unity XR 3D Model
- [ ] Well pump `.glb`/`.fbx` CAD model imported
- [ ] `GDCAssetController.cs` attached to all 50 asset GameObjects
- [ ] `ColourController.cs` — green/amber/red state transitions working
- [ ] WebSocket connected to FastAPI stream
- [ ] WebGL build exported to `unity/GDC_Plant_Twin/Builds/WebGL/`

### Step 4 — LSTM Training
- [ ] `datasets/Sensor_Readings.xlsx` exported to Watson Studio COS bucket
- [ ] `ml/lstm/notebooks/01_lstm_training.ipynb` executed successfully
- [ ] AUC-ROC ≥ 0.82 achieved and documented
- [ ] Model deployed as Watson ML REST endpoint
- [ ] `/predict/failure` API endpoint integrated

### Step 5 — Monte Carlo with Weibull
- [ ] Weibull shape (k) and scale (λ) parameters calibrated per asset class
- [ ] Normal distributions replaced in `monte_carlo/engine.py`
- [ ] Sensor covariate modifiers (temperature, vibration → Weibull scale shift)
- [ ] 10,000 runs complete in < 5s (benchmark documented)

### Step 6 — What-If in Unity
- [ ] Unity slider prefabs created for temp/pressure/vibration
- [ ] Slider values POST to `/whatif/simulate`
- [ ] Risk gauge updates in < 2s
- [ ] Probability readout matches API response

### Step 7 — CNN Anomaly AI
- [ ] Unity screenshot dataset captured (min 500 images per class)
- [ ] `ml/cnn_anomaly/notebooks/01_cnn_training.ipynb` executed
- [ ] Accuracy ≥ 80% on test set
- [ ] REST endpoint deployed, Unity polling every 5s

### Step 8 — Maintenance Scheduler
- [ ] `scheduler/optimizer.py` implemented with scipy.optimize or PuLP
- [ ] All constraints validated (crew, interdependencies, regulatory)
- [ ] 90-day Gantt chart rendered in React dashboard
- [ ] Maximo work orders created via `maximo/workorder_client.py`

### Step 9 — OpenShift Deployment
- [ ] Namespace `ot-digital-twin` created
- [ ] All secrets created (`maximo-credentials`, `watson-credentials`)
- [ ] `kustomize build` applies cleanly
- [ ] All pods in Running state
- [ ] Public Route URL accessible and TLS working
- [ ] Health endpoints `/health` and `/ready` returning 200

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| TechZone reservation takes >48h | Medium | High | Reserve immediately; Asenath to escalate via Collins Curtis |
| Unity `.glb` import breaks on WebGL | Medium | High | Test on Three.js viewer first; keep fallback Three.js viewer for demo |
| LSTM AUC-ROC < 0.82 on first run | Medium | Medium | Class weighting, SMOTE oversampling, tune sequence length |
| Maximo REST API schema differs from expected | High | High | Validate with Swagger UI on TechZone instance before coding |
| OpenShift image pull fails (private registry) | Low | High | Push to IBM Cloud Container Registry; configure ImagePullSecret |
| Demo environment cold start latency | Medium | Medium | Warmup script; keep replicas: 2 minimum |

---

## Next Actions (28 March 2026)

1. **Wisdom** — Run this script, commit structure to `dev` branch
2. **Wisdom** — Reserve TechZone: Maximo MAS 9.1 SNO + Watson Studio + OCP
3. **Wisdom** — Generate `datasets/GDC_Assets.xlsx` (50 rows, all columns)
4. **Asenath** — Unblock IBM Cloud credentials via Collins Curtis (TechZone Lab Manager)
5. **Asenath** — Begin Step 5: Weibull parameter research for well pump asset class
6. **Maurine** — Begin Step 3: Import well pump CAD model into Unity, test WebGL export
