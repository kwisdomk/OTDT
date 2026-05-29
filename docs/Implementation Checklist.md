# OTDT Checklist

This is the shared progress checklist for OTDT. Update it as work is completed
or verified.

**Original sources:** `OT_Digital_Twin_Build_Guide.docx`,
`OT_Digital_Twin_Build_Deck.pptx`, `OT_Digital_Twin_MVP_Tracker.xlsx`

**Status keys:** Done | Partial | Pending | Blocked | Paused

**Important:** IBM platform work is paused for now, but remains part of the
original OTDT plan.

## Current Summary

| Area | Status | Last checked | Notes |
| --- | --- | --- | --- |
| Step 0 / baseline lock | Done | 2026-05-28 | Baseline artifacts confirmed and repository governance updated |
| Documentation index created | Done | 2026-05-28 | `DOCUMENTATION_INDEX.md` established |
| Original baseline protected in repo | Done | 2026-05-28 | `Product Baseline.md`, `Decision Log.md`, `AGENTS.md` updated |
| WP-07 demo values: 34% -> 68% -> USD 122,400 | Done | 2026-05-26 | Verified on calibrated local demo route |
| Unity stream sensor field repair | Done | 2026-05-26 | Baseline sensor keys restored in fallback stream |
| React support UI | Partial | 2026-05-26 | Tests/build pass; supporting UI only, not original Three.js viewer |
| Unity experience | Partial | 2026-05-26 | Scripts/project exist; running visual verification still needed |
| LSTM model | Partial | 2026-05-26 | March model artifacts exist; accepted metric/spec validation pending |
| Monte Carlo engine | Partial | 2026-05-29 | Code exists; calibrated demo route accepts Unity `deferral_days` payload; engine-backed What-If still differs |
| Scheduler | Blocked | 2026-05-26 | Runs, but currently flags all 50 assets as critical |
| IBM integrations and cloud training | Paused | 2026-05-26 | Resume only when project owner says so |
| GitHub push of current recovery commit | Pending | 2026-05-26 | Local branch ahead by commit `bc785dfd` |

## 1. Setup And Tools

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| Unity project available locally | Partial | 2026-05-26 | Project/scripts found; open-and-run check pending |
| Python environment runs local API/demo checks | Done | 2026-05-26 | Compile/demo assertions passed |
| Docker Compose configuration parses | Done | 2026-05-26 | `docker compose config --quiet` passed |
| Three.js browser viewer tooling/project exists | Pending | 2026-05-26 | Original requirement; no verified implementation |
| Watson Studio / watsonx environment usable | Paused | 2026-05-26 | Project creation blocker |
| Maximo environment usable | Paused | 2026-05-26 | IBM work held |

## 2. Original Data And Sensor Flow

Original intended flow:

```text
Synthetic Sensor_Readings -> Watson IoT / Kafka -> Maximo Monitor
-> FastAPI sensor bridge -> Unity XR / Three.js viewer
```

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| Original workbook is the data source to follow | Done | 2026-05-26 | Recorded in baseline/decision log |
| 50 assets verified, including `GDC-WP-007` | Done | 2026-05-26 | Verified from original tracker |
| Data-tab roles identified (`Sensor_Readings`, `Failure_History`, `MC_Validation`) | Done | 2026-05-26 | Verified from original tracker |
| Confirm final `Sensor_Readings` row count | Blocked | 2026-05-26 | Source wording and workbook row count differ |
| Align runtime sensor field names/calibration | Blocked | 2026-05-26 | Mixed baseline and legacy fields still exist |
| Load assets/sensors into Maximo | Paused | 2026-05-26 | IBM work held |
| Verify FastAPI latest-sensor endpoint under 500 ms | Pending |  |  |
| Verify complete live/event-stream pipeline | Paused | 2026-05-26 | IBM work held |

## 3. Unity And Browser Visualisation

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| Unity scripts/project present | Partial | 2026-05-26 | Sensor bridge, HUD, colour, camera, asset selector and What-If scripts found |
| Fallback stream uses Unity sensor keys | Done | 2026-05-26 | `temperature_c`, `pressure_bar`, `vibration_mm_s`, `flow_rate_kg_s`, `rotation_rpm` |
| Run Unity scene and confirm sensors update visually | Pending |  |  |
| Confirm all 50 assets map/select correctly in Unity | Pending |  |  |
| Confirm green/amber/red asset colour changes | Pending |  |  |
| Confirm sensor overlay and trend display in Unity | Pending |  |  |
| Implement/verify required Three.js browser viewer | Pending |  | Original browser visualisation requirement |
| React dashboard support view | Partial | 2026-05-26 | Compiles and tests pass; do not treat as Three.js completion |

## 4. LSTM Failure Predictor

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| Existing March model files located | Partial | 2026-05-26 | `.h5`, scaler and feature config present |
| Preserve report that model was trained for March presentation | Done | 2026-05-26 | Owner-reported history; not new model validation |
| Decide approved LSTM configuration | Blocked | 2026-05-26 | PDF and tracker specifications differ |
| Validate model using original data and approved specification | Pending |  |  |
| Confirm AUC-ROC > 0.82 | Pending |  | Original target |
| Confirm calibration curve/output | Pending |  | Original requirement |
| Confirm SavedModel and ONNX export | Pending |  | Original requirement |
| New Watson Studio retraining | Paused | 2026-05-26 | Do not run pending IBM reactivation |

## 5. Monte Carlo Simulation

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| Monte Carlo engine code exists | Partial | 2026-05-26 | `monte_carlo/engine.py` |
| Calibrated demo route returns WP-07 34% -> 68% | Done | 2026-05-26 | Verified locally |
| Calibrated demo route returns USD 122,400 expected cost | Done | 2026-05-26 | Verified locally |
| Fit/confirm Weibull distributions from original failure history | Pending |  |  |
| Validate against original `MC_Validation` cases | Pending |  |  |
| Benchmark 10,000 runs under 5 seconds | Pending |  | Original target |
| Align engine-backed What-If result with original demo | Blocked | 2026-05-26 | Separate route returned about 56% at 45 days |
| Cloud/OpenShift deployment | Paused | 2026-05-26 | IBM work held |

## 6. What-If Interface

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| Unity What-If API contract accepts `deferral_days` | Done | 2026-05-29 | OTD-014: `/api/monte-carlo/whatif` accepts both `deferral_days` and `maintenance_date`; 18/18 function checks and 22/22 HTTP checks passed |
| What-If HTTP verification passed | Done | 2026-05-29 | Manual ASGI-transport verification (22/22 checks); temporary scripts removed after pytest suite added |
| What-If automated pytest suite | Pending | 2026-05-29 | `api/tests/test_whatif_contract.py` (6 tests); requires `pip install -r api/requirements-dev.txt` in API venv |
| Unity What-If script exists for WP-07 | Partial | 2026-05-26 | `WhatIfSlider.cs` present; sends `{ asset_id, deferral_days }` matching API contract |
| Verify slider renders from 0 to 180 days in Unity | Pending |  | Requires Unity Editor play-mode |
| Verify UI changes 34% to 68% at 45 days | Partial | 2026-05-29 | API value verified via HTTP; Unity display not rerun |
| Verify USD cost overlay in Unity | Pending |  |  |
| Verify response time under 2 seconds | Pending |  | Original target |

## 7. Anomaly AI

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| Capture Unity normal/anomalous screenshots | Pending |  | Original plan: 200 screenshots |
| Train CNN / ResNet-18 visual detector | Paused | 2026-05-26 | Watson training held |
| Confirm accuracy >80% | Pending |  | Original target |
| Show red visual alert ring in Unity | Pending |  |  |
| Clearly label any rule-based fallback as simplified MVP | Pending |  | Do not claim it is CNN training |

## 8. Maintenance Scheduler

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| Scheduler code exists | Partial | 2026-05-26 | `scheduler/optimizer.py` and Gantt code found |
| Scheduler test runs from correct repo path | Done | 2026-05-26 | Path repaired and script executed |
| Generate acceptable 90-day schedule | Blocked | 2026-05-26 | Current run marked all 50 assets critical |
| Show Gantt schedule in Unity | Pending |  | Original requirement |
| Create priority Maximo work orders | Paused | 2026-05-26 | IBM work held |
| Reproduce showcase: identify three out-of-plan high-risk assets | Blocked | 2026-05-26 | Current calibration does not do this |

## 9. Demo And Delivery

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| March showcase was presented/run | Done | March 2026 | Owner-reported; exact run time not recorded |
| Current local Scenario 1 value: WP-07 at 34% | Done | 2026-05-26 | Verified in local demo path |
| Current local Scenario 2 calculation: 45 days -> 68% / USD 122,400 | Done | 2026-05-26 | Verified in local demo path |
| Scenario 2 verified in running Unity display | Pending |  |  |
| Scenario 3 scheduler story verified | Blocked | 2026-05-26 | Scheduler calibration issue |
| Annual ROI statement retained: USD 360,000 vs USD 48,000 = 650% | Partial | 2026-05-26 | Baseline preserved; runnable display evidence pending |
| Push recovery commit to GitHub | Pending | 2026-05-26 | Commit `bc785dfd` exists locally |

## Latest Work Log

| Date / time (EAT) | Work | Result |
| --- | --- | --- |
| 2026-05-29 10:55 | Timeline interpretation governance (OTD-015) | Baseline, Decision Log, and Checklist updated: timeline dates are planning context; product behaviour requirements remain hard |
| 2026-05-29 10:50 | What-If test hygiene (Step 2.1) | Created `api/requirements-dev.txt` (pytest, pytest-asyncio, httpx); added `api/tests/__init__.py`; removed temporary `verify_whatif.py` and `verify_whatif_http.py`; pytest pending dependency install |
| 2026-05-29 09:50 | What-If API contract fix (OTD-014) | `deferral_days` accepted; 18/18 function + 22/22 HTTP checks passed; docs updated |
| 2026-05-26 23:40 | Baseline recovery commit `bc785dfd` created | Unity fallback stream, WP-07 values, governance and tests committed locally |
| 2026-05-26 | Python checks, React tests/build and Compose parse | Passed for committed recovery work |
| 2026-05-26 | Scheduler validation | Runs, but calibration/output not accepted |
| 2026-05-26 | IBM integration/training work | Paused until otherwise directed |

## How To Update

When a task is finished or tested, change its status and fill in:

```text
Status: Done / Partial / Pending / Blocked / Paused
Date checked: YYYY-MM-DD
Notes: what was tested or what is still missing
```
