# OTDT Long Engineering Smoke Test Runbook

Purpose: run a broader local smoke test of the current OTDT stack and record what works, what falls back, and what remains blocked.

This is the long method. It is for engineering validation, not for a quick stakeholder visual demo. It intentionally checks more surfaces than the short Unity path, including API endpoints, optional React dashboard startup, optional live sensor publishing, Unity, and the scheduler current state.

## What This Runs

1. Repository and environment pre-flight checks.
2. Optional development test dependency install.
3. FastAPI backend.
4. API endpoint smoke tests.
5. Optional Kafka sensor publisher, if Kafka is running.
6. Optional React dashboard.
7. Unity project.
8. Scheduler current-state check.

## Known Current-State Interpretation

- The calibrated What-If API route is expected to pass.
- The API may fall back to synthetic prediction if the local LSTM model shape does not match the runtime input.
- Kafka is optional for this runbook because the API has fallback/mock streaming.
- Scheduler currently runs but is known to be misaligned: it may mark all 50 assets critical. That is a Step 3 blocker, not a startup failure.

## Step 1: Open PowerShell At Repo Root

```powershell
cd "Q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT"
```

## Step 2: Pre-Flight Checks

```powershell
git branch --show-current
git log -n 1 --oneline
.\venv\Scripts\python.exe --version
node -v
npm -v
```

Expected:

- Branch should be `feat/event-hardening` unless intentionally changed.
- Recent committed baseline should include `ba3e7521` or a later commit.
- Python venv should be available at `.\venv\Scripts\python.exe`.
- Node and npm should be available if testing React.

Confirm baseline files exist:

```powershell
Test-Path "OT_Digital_Twin_Build_Guide.docx"
Test-Path "OT_Digital_Twin_Build_Deck.pptx"
Test-Path "OT_Digital_Twin_MVP_Tracker.xlsx"
Test-Path "datasets/GDC_Assets.xlsx"
```

Each command should return:

```text
True
```

## Step 3: Optional Dev Test Dependencies

Only run this if you want to execute the What-If pytest suite.

```powershell
.\venv\Scripts\pip.exe install -r api\requirements-dev.txt
```

Then run:

```powershell
.\venv\Scripts\python.exe -m pytest api\tests\test_whatif_contract.py -v
```

Expected:

```text
passed
```

If `pytest` is not installed and you do not want to install dev dependencies, skip this step.

## Step 4: Quick Local Verification

```powershell
.\venv\Scripts\python.exe verify.py
```

Expected output:

```text
Config OK
[WS] Asset loader ready - 50 assets
Predict OK
Whatif OK
```

## Step 5: Start The API

Open a dedicated PowerShell terminal:

```powershell
cd "Q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT"
.\venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected:

- API runs at `http://127.0.0.1:8000`.
- Swagger docs are available at `http://127.0.0.1:8000/docs`.
- Startup may take time if TensorFlow imports.
- Missing Kafka, Redis, or TimescaleDB should not stop the local fallback path.

## Step 6: API Smoke Tests

Open a second PowerShell terminal.

Health:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

Expected:

```text
status: ok
```

What-If, 0 days:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/monte-carlo/whatif" -Method Post -ContentType "application/json" -Body '{"asset_id":"GDC-WP-007","deferral_days":0}'
```

Expected:

```text
deferred_failure_probability: 0.34
expected_failure_cost_usd: 61200
```

What-If, 45 days:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/monte-carlo/whatif" -Method Post -ContentType "application/json" -Body '{"asset_id":"GDC-WP-007","deferral_days":45}'
```

Expected:

```text
deferred_failure_probability: 0.68
expected_failure_cost_usd: 122400
```

Anomaly status:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/anomaly/status/GDC-WP-007" -Method Get
```

Expected current demo behavior:

```text
classification: ANOMALY
```

Predict endpoint:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/predict/failure/GDC-WP-007" -Method Get
```

Expected current demo behavior:

```text
failure_probability: 0.34
```

Note: this may be served by synthetic fallback if the local LSTM model cannot accept the current runtime feature shape.

Agent trigger:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/agent/test-trigger" -Method Post
```

Expected:

```text
risk assessment payload for GDC-WP-007
```

## Step 7: Optional Live Sensor Publisher

Only run this if Kafka is already running and reachable.

Open a third PowerShell terminal:

```powershell
cd "Q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT"
$env:KAFKA_BROKER="localhost:29092"
.\venv\Scripts\python.exe sensor_simulator\kafka_publisher.py --demo
```

Expected:

```text
[KAFKA] Publishing to localhost:29092 topic sensor.telemetry
[KAFKA] Sent: ...
```

If Kafka is not running, this publisher will fail. That does not block the fallback API plus Unity path.

## Step 8: Optional React Dashboard

Open a new PowerShell terminal:

```powershell
cd "Q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT\frontend\react-dashboard"
npm start
```

Open:

```text
http://localhost:3000
```

Expected:

- React dashboard starts.
- It uses API configuration from `.env.local`.
- It connects to the API at `http://localhost:8000`.

## Step 9: Unity Check

Open Unity Hub and open:

```text
Q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT\unity\GDC_Plant_Twin
```

Open scene:

```text
Assets\GDCPlantScene.unity
```

Press Play.

Expected:

- Unity connects to `ws://localhost:8000/twin/stream`.
- Sensor visualization updates from live Kafka data if Kafka is running, otherwise from API fallback stream.
- WP-07 What-If slider reaches `34%` at 0 days and `68%` at 45 days.

## Step 10: Scheduler Current-State Check

Run from repo root:

```powershell
cd "Q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT"
.\venv\Scripts\python.exe scheduler\test_scheduler.py
```

Expected current behavior:

- Script completes.
- It may report all 50 assets as critical.
- This is a known Step 3 scheduler alignment blocker.

This result should be recorded honestly. It means the scheduler runs, but it does not yet meet the baseline demo requirement of focused high-risk assets and top-five Maximo work-order candidates.

## Step 11: Shutdown

Stop Unity Play Mode.

Press `Ctrl + C` in each terminal running:

- API / Uvicorn
- React dashboard
- Kafka publisher

If ports remain occupied:

```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force -ErrorAction SilentlyContinue
Stop-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess -Force -ErrorAction SilentlyContinue
```

## Pass / Fail Checklist

| Component | Command Or Step | Expected Result | Current Known Status |
|---|---|---|---|
| Pre-flight | `verify.py` | Config, assets, predict, What-If OK | Expected pass |
| API | `uvicorn api.main:app` | Runs on port 8000 | Expected pass |
| Health | `/health` | `status: ok` | Expected pass |
| What-If 0 days | `/api/monte-carlo/whatif` | 34% | Expected pass |
| What-If 45 days | `/api/monte-carlo/whatif` | 68%, USD 122,400 | Expected pass |
| Anomaly | `/api/anomaly/status/GDC-WP-007` | `ANOMALY` | Expected pass or fallback |
| Predict | `/api/predict/failure/GDC-WP-007` | 34% | Expected pass via fallback if needed |
| Kafka publisher | `kafka_publisher.py --demo` | Publishes telemetry | Optional, requires Kafka |
| React dashboard | `npm start` | Opens localhost:3000 | Optional |
| Unity | Play scene | Visual twin updates | Expected pass after API starts |
| Scheduler | `scheduler\test_scheduler.py` | Runs schedule | Runs, but currently misaligned |

## Summary

This long method is for finding integration truth. It intentionally exposes fallback behavior and known blockers.

Use the short runbook for quick Unity demonstration. Use this long runbook before implementation work or before claiming full baseline readiness.
