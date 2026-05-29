# OTDT Short Unity Demo Runbook

Purpose: quickly run the OTDT Unity visualization path for a local demo.

This is the short method. It is intended for showing the digital twin visually, not for proving every baseline requirement. It starts the FastAPI backend and opens the Unity scene. The API can provide fallback/mock sensor streaming, so Kafka is not required for this path.

## What This Runs

1. Optional pre-flight verification with `verify.py`.
2. FastAPI backend on `http://127.0.0.1:8000`.
3. Unity project `unity/GDC_Plant_Twin`.
4. Unity WebSocket connection to `ws://localhost:8000/twin/stream`.
5. Unity What-If slider calls `http://localhost:8000/api/monte-carlo/whatif`.

## What This Does Not Prove

- It does not validate the scheduler.
- It does not prove live Kafka telemetry is running.
- It does not prove the LSTM model artifact is correctly serving real inference.
- It does not prove the CNN model is trained.
- It does not prove Maximo live integration.

## Step 1: Open PowerShell At Repo Root

```powershell
cd "Q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT"
```

## Step 2: Optional Pre-Flight Check

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

If this fails, check that the virtual environment exists at `.\venv\Scripts\python.exe` and that the repo is opened from the OTDT root.

## Step 3: Start The API

Open a dedicated PowerShell terminal and run:

```powershell
cd "Q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT"
.\venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected behavior:

- API listens on `http://127.0.0.1:8000`.
- Swagger docs are available at `http://127.0.0.1:8000/docs`.
- Unity WebSocket feed is available at `ws://localhost:8000/twin/stream`.
- Startup may print warnings for unavailable Kafka, Redis, TimescaleDB, or LSTM model shape mismatch. For the short Unity demo path, those warnings are acceptable if the API keeps running.

## Step 4: Optional API Health Check

Open a second PowerShell terminal:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

Expected response includes:

```text
status: ok
```

## Step 5: Optional What-If Checks

Check the baseline WP-07 values before opening Unity:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/monte-carlo/whatif" -Method Post -ContentType "application/json" -Body '{"asset_id":"GDC-WP-007","deferral_days":0}'
```

Expected:

```text
deferred_failure_probability: 0.34
expected_failure_cost_usd: 61200
```

Then check 45-day deferral:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/monte-carlo/whatif" -Method Post -ContentType "application/json" -Body '{"asset_id":"GDC-WP-007","deferral_days":45}'
```

Expected:

```text
deferred_failure_probability: 0.68
expected_failure_cost_usd: 122400
```

## Step 6: Open Unity

Open Unity Hub and open this project:

```text
Q:\ibm\EAAAIW @ IBM Research Lab Africa\OTDT\unity\GDC_Plant_Twin
```

Open this scene:

```text
Assets\GDCPlantScene.unity
```

## Step 7: Run Unity Play Mode

Press Play in Unity Editor.

Expected behavior:

- Unity connects to `ws://localhost:8000/twin/stream`.
- Plant assets display live/fallback sensor state.
- WP-07 / `GDC-WP-007` is available for the demo.
- The What-If slider calls `http://localhost:8000/api/monte-carlo/whatif`.
- At 0 deferral days, WP-07 shows about `34%`.
- At 45 deferral days, WP-07 shows about `68%` and expected failure cost `USD 122,400`.

## Step 8: Stop The Demo

Stop Unity Play Mode.

In the API PowerShell terminal, press:

```text
Ctrl + C
```

If port `8000` remains occupied:

```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force -ErrorAction SilentlyContinue
```

## Summary

This short method is the fastest local visual demo path:

```text
verify.py optional -> start FastAPI -> open Unity -> press Play
```

It is valid for visual demonstration, but it is not a full engineering validation of OTDT.
