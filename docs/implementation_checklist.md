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
| Documentation index created | Done | 2026-05-28 | `docs/documentation_index.md` established |
| Original baseline protected in repo | Done | 2026-05-28 | `product_baseline.md`, `Decision Log.md`, `AGENTS.md` updated |
| WP-07 demo values: 34% -> 68% -> USD 122,400 | Done | 2026-05-26 | Verified on calibrated local demo route |
| Unity stream sensor field repair | Done | 2026-05-26 | Baseline sensor keys restored in fallback stream |
| React support UI | Partial | 2026-05-26 | Tests/build pass; supporting UI only, not original Three.js viewer |
| Unity experience | Partial | 2026-05-29 | Short demo path verified manually; full production readiness not claimed |
| LSTM model | Partial | 2026-05-29 | Tracker-aligned 720x8 model trained and locally evaluated (AUC 0.9857); unapproved API wiring reverted (OTD-017); fallback remains active; safe API wiring pending |
| Monte Carlo engine | Partial | 2026-05-29 | Code exists; calibrated demo route accepts Unity `deferral_days` payload; engine-backed What-If still differs |
| Scheduler | Partial | 2026-05-29 | Demo risk profile aligned: 3 critical, 90-day window, top-five work orders; data limitation documented |
| IBM integrations and cloud training | Paused | 2026-05-26 | Resume only when project owner says so |
| GitHub push of current recovery commit | Done | 2026-05-30 | `feat/event-hardening` is synced with origin at `bfc35b59`; `main` merge remains pending |
| Legacy tracked model/notebook artifacts | Pending | 2026-05-30 | Four older `.h5`/`.pkl`/`.ipynb` files remain tracked; cleanup is a supporting implementation decision, not a baseline requirement; see OTD-018 |

## 1. Setup And Tools

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| Unity project available locally | Done | 2026-05-29 | Scene opens; assets render; short demo path verified |
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
| Run Unity scene and confirm sensors update visually | Partial | 2026-05-29 | Short demo: assets render, WP-07 selectable showing CAUTION, GDC-WP-011 showed normal (8%); full 50-asset visual sweep not performed |
| Confirm all 50 assets map/select correctly in Unity | Pending |  | Short demo verified WP-07 and WP-011 selection; full 50-asset click-through not performed |
| Confirm green/amber/red asset colour changes | Partial | 2026-05-29 | WP-07 displayed CAUTION state; green/normal observed on other assets; systematic colour test not performed |
| Confirm sensor overlay and trend display in Unity | Pending |  |  |
| Implement/verify required Three.js browser viewer | Pending |  | Original browser visualisation requirement |
| React dashboard support view | Partial | 2026-05-26 | Compiles and tests pass; do not treat as Three.js completion |

## 4. LSTM Failure Predictor

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| Existing March model files located | Partial | 2026-05-26 | `.h5`, scaler and feature config present |
| Preserve report that model was trained for March presentation | Done | 2026-05-26 | Owner-reported history; not new model validation |
| Decide approved LSTM configuration | Done | 2026-05-29 | Tracker-aligned 720x8 model accepted as current candidate artifact |
| Validate model using original data and approved specification | Partial | 2026-05-29 | Tracker-aligned model trained and fitted scaler recreated; unapproved API wiring reverted (OTD-017); fallback remains active; safe wiring pending approval |
| Confirm AUC-ROC > 0.82 | Done | 2026-05-29 | Test AUC-ROC is 0.9857 (with overlapping-window caveat) |
| Confirm calibration curve/output | Pending |  | Platt calibration is baseline-required; implementation decisions unresolved |
| Confirm SavedModel and ONNX export | Pending |  | ONNX/SavedModel still pending |
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
| Verify slider renders from 0 to 180 days in Unity | Partial | 2026-05-29 | Slider tested at 0, 45, and 112 days; full 0–180 sweep not performed |
| Verify UI changes 34% to 68% at 45 days | Done | 2026-05-29 | Unity slider at 0 days: 34.0% / $61,200; at 45 days: 68.0% / $122,400; at 112 days: 83.9% / $150,984 |
| Verify USD cost overlay in Unity | Done | 2026-05-29 | Displayed $61,200 at 0 days, $122,400 at 45 days, $150,984 at 112 days |
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
| Generate acceptable 90-day schedule | Partial | 2026-05-29 | 90-day window, 3 critical, 33 scheduled, 17 skipped; data limitation documented |
| Show Gantt schedule in Unity | Pending |  | Original requirement |
| Create priority Maximo work orders | Paused | 2026-05-26 | IBM work held |
| Reproduce showcase: identify three out-of-plan high-risk assets | Partial | 2026-05-29 | GDC-WP-007 (34%), GDC-TU-001 (36%), GDC-TU-010 (32%); dataset does not provide three clean assets due outside the 90-day window |

## 9. Demo And Delivery

| Task | Status | Date checked | Notes |
| --- | --- | --- | --- |
| March showcase was presented/run | Done | March 2026 | Owner-reported; exact run time not recorded |
| Current local Scenario 1 value: WP-07 at 34% | Done | 2026-05-26 | Verified in local demo path |
| Current local Scenario 2 calculation: 45 days -> 68% / USD 122,400 | Done | 2026-05-26 | Verified in local demo path |
| Scenario 2 verified in running Unity display | Done | 2026-05-29 | Unity slider at 0 days: 34.0%; at 45 days: 68.0% / $122,400; short demo path |
| Scenario 3 scheduler story verified | Partial | 2026-05-29 | Demo risk profile aligned; full production scheduler not validated |
| Annual ROI statement retained: USD 360,000 vs USD 48,000 = 650% | Partial | 2026-05-26 | Baseline preserved; runnable display evidence pending |
| Push recovery commit to GitHub | Done | 2026-05-30 | `feat/event-hardening` is synced with origin at `bfc35b59`; `main` merge remains pending |

## Latest Work Log

| Date / time (EAT) | Work | Result |
| --- | --- | --- |
| 2026-05-30 05:17 | Read-only state audit against baseline docs | Checklist push status corrected; legacy tracked artifact issue recorded as pending OTD-018; no code cleanup performed |
| 2026-05-29 22:42 | Revert unapproved LSTM API wiring (OTD-017) | Commit `cb6c0c9b` reverted by `b5e2d5f1`; `api/routers/predict.py` restored, `api/tests/test_predict_tracker_contract.py` removed; backup branch `backup/unapproved-lstm-wiring-cb6c0c9b` created; fallback remains active; revert pushed to origin |
| 2026-05-29 21:15 | Prepare and commit safe LSTM readiness documentation | Safe metadata, .gitignore, and model readiness documented and committed under OTD-016 |
| 2026-05-29 14:30 | Unity short demo verification | Scene runs, assets render, WP-07 selectable (CAUTION), What-If slider: 0d=34%/$61,200, 45d=68%/$122,400, 112d=83.9%/$150,984; GDC-WP-011 normal at 8%; short demo path verified, not full production readiness |
| 2026-05-29 14:00 | Scheduler alignment commit `e5b0e0ac` pushed | 3 critical, 90-day window, top-five work orders; dataset limitation documented |
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
