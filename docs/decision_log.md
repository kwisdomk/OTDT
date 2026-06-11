# Product Decision Log: OT Digital Twin

## How To Use This Log

This log records decisions that interpret, extend, or revise the authoritative
baseline in `docs/product_baseline.md`.

Do not record routine bug fixes or refactors here. Add an entry when a change:

- Resolves an ambiguity in the original sources.
- Adds a product capability that could be mistaken for original scope.
- Changes an asset, agent, metric, demo scenario, target client, dataset, or
  business claim.
- Accepts an implementation architecture decision that affects project
  documentation or external communication.

Each decision must identify who approved it. Until approval is recorded, an
open issue remains open and must not be presented as a settled product fact.

## Open Issues

| ID | Issue | Baseline evidence | Status |
| --- | --- | --- | --- |
| OTD-001 | Sensor_Readings row count / date-range conflict: described as 43,800 records / five years, but the root workbook contains 87,600 rows for one year. | Root workbook physical row count vs. documentation labels. | Open: owner confirmation required. |
| OTD-002 | Mixed sensor schemas across codebase. (Legacy-key consumers vs baseline keys). | Workbook `Sensor_Readings` column headers versus current code sensor key names. | Open: contract migration required. |
| OTD-003 | Sensor meaning and calibration differ. Runtime datasets differ from root tracker values. | Original tracker inspection, repository comparison. | Open: align runtime datasets without overriding the original tracker. |
| OTD-006 | LSTM runtime model/API feature mismatch (configuration conflict between docs and tracker). | Original docs vs original workbook `AI_Model_Specs`. | Resolved: Configuration resolved; unapproved API wiring attempt reverted (OTD-017). Safe API wiring remains pending. |
| OTD-009 | Unity What-If API contract mismatch: two What-If paths do not produce the same showcase result. | Local execution comparison. | Resolved: calibrated demo route now accepts Unity `deferral_days` payload. See OTD-014. |
| OTD-010 | Scheduler currently marks all 50 assets critical, rather than identifying three high-risk assets. | Local execution of `scheduler/test_scheduler.py`. | Partial: demo risk profile aligned (commit `e5b0e0ac`, 2026-05-29). 3 critical, 90-day window, top-five work orders. Dataset limitation documented. Full production validation pending. |
| OTD-011 | Failure mode taxonomy conflict: docs imply limited Weibull fits, root workbook contains 14 failure modes. | Root workbook vs documentation. | Open: owner confirmation required. |
| OTD-012 | WP-07 cost policy conflict: tracker/runtime/demo values differ, though demo narrative requires USD 180,000 and USD 122,400. | Tracker, runtime code, and demo narrative comparison. | Open: owner confirmation required on consistent cost policy. |
| OTD-018 | Legacy model binary and notebook files remain tracked in git despite current ignore policy. | `git ls-files --cached` on 2026-05-30 showed four older `.h5`/`.pkl`/`.ipynb` files still tracked. The three governing docs do not define git artifact-tracking policy. | Resolved: owner approved supporting implementation cleanup; files removed from git tracking only, local copies preserved. |

## Approved Decisions

### OTD-020: Calibrated LSTM Prediction API Wiring

- Date: 2026-06-11
- Classification: Supporting implementation
- Decision: The tracker-aligned 720×8 LSTM model with Platt calibration (OTD-016, OTD-019) is wired into `POST /api/predict/failure` as an optional industrial prediction path. Owner decisions applied:
  - **Activation:** Requires a valid 720×8 `sensor_sequence` field and/or explicit `force_source="tracker_lstm"`. Without `sensor_sequence`, the tracker path is never entered and existing fallback behaviour is unchanged.
  - **Priority chain:** Watson ML → Tracker LSTM → Local .h5 → Synthetic. Tracker slot only activates when `sensor_sequence` is present.
  - **Isolation:** No changes to the Unity What-If demo route (`/api/monte-carlo/whatif`), Weibull engine (`/whatif/simulate`), Monte Carlo engine, or scheduler. LSTM is not wired into Monte Carlo in this scope.
  - **No demo force_source flag:** The existing calibrated demo route is already protected; adding a demo flag was rejected to reduce misuse risk.
  - **Failure behaviour:** Explicit `force_source="tracker_lstm"` fails loudly (HTTP 422 for missing/invalid sequence, HTTP 503 for missing artifacts). Implicit attempts (no `force_source`) fall through silently to synthetic.
  - **Output:** `failure_probability` is the Platt-calibrated value. Response includes `raw_score`, `calibrated_score`, `calibration_applied`, `is_synthetic`, `model_source="local_tracker_720x8_platt"`.
  - **Artifact loading:** Local filesystem loading from `ml/lstm/models/tracker_720x8/` (.keras model, fitted .pkl scaler, .json Platt coefficients) at API startup. Each artifact loads independently; missing artifacts do not crash the API.
- Baseline impact: No baseline revision. Implements the baseline-required LSTM failure predictor without changing any demo value, agent scope, acceptance target, or Unity contract.
- Evidence: Combined pytest run on 2026-06-11 (EAT 16:53): 31/31 passed across four suites — `test_whatif_contract.py` (6), `test_predict_tracker_contract.py` (10), `test_demo_guardrails.py` (6), `test_platt_transform.py` (9). Protected demo values verified: WP-07 0-day=34%/$61,200, 45-day=68%/$122,400, 112-day≈83.9%/$150,984. GET WP-07 returns 0.34 synthetic. Weibull engine returns ~0.56 at 45 days (not forced to 0.68). `git status --short` confirms only `api/routers/predict.py` (modified), `api/tests/test_predict_tracker_contract.py` (new), `api/tests/test_demo_guardrails.py` (new) are planned changes.
- Approved by: Project owner (decisions recorded in conversation a991559c on 2026-06-09)
- Affected files/components: `api/routers/predict.py` (modified), `api/tests/test_predict_tracker_contract.py` (new), `api/tests/test_demo_guardrails.py` (new).

### OTD-019: Platt Calibration Artifact Policy

- Date: 2026-05-30
- Classification: Supporting implementation
- Decision: The following implementation choices for Platt calibration are approved. The three governing documents require Platt calibration (`AI_Model_Specs` in the tracker) but do not specify artifact format, split policy, raw-score domain, or fit strategy:
  - **Artifact format:** Separate JSON metadata file beside the local tracker model (`lstm_tracker_720x8_calibration.json`).
  - **Fitting split:** Validation split only (1007 windows, 36 positive).
  - **Evaluation split:** Test split only (1007 windows, 36 positive).
  - **Raw-score domain:** Raw model probability output in (0, 1).
  - **Equation:** `calibrated_probability = sigmoid(coefficient * raw_score + intercept)` where `sigmoid(x) = 1 / (1 + exp(-x))`.
  - **Fit strategy:** `sklearn.linear_model.LogisticRegression(C=1e10)` on raw model probabilities, with stratified 70/15/15 split (random_state=42) matching the original metadata's documented `stratified sliding windows` strategy.
  - **First scope:** Artifact generation and pure-function math test only. Runtime wiring (API, Monte Carlo) is not approved in this scope.
- Baseline impact: No baseline revision. Platt calibration is baseline-required; these choices implement it without changing any product fact, demo value, or agent scope.
- Evidence: Calibration artifact generated on 2026-05-30. Test-split Brier score improved from 0.0286 (raw) to 0.0179 (calibrated). AUC-ROC 0.9745 (unchanged, as expected from monotonic transform). Coefficient 10.2520, intercept −9.3951.
- Approved by: Project owner (approved implementation choices and Option A raw-score domain)
- Affected files/components: `ml/lstm/scripts/create_platt_calibration.py` (new), `ml/lstm/scripts/test_platt_transform.py` (new), `ml/lstm/models/tracker_720x8/lstm_tracker_720x8_calibration.json` (new, git-trackable JSON metadata; model binaries and notebooks remain ignored).

### OTD-018: Remove Legacy Model And Notebook Artifacts From Git Tracking

- Date: 2026-05-30
- Classification: Supporting implementation
- Decision: Remove four legacy model/notebook artifacts from git tracking using index-only cleanup while preserving local working-tree copies: `ml/cnn_anomaly/notebooks/01_cnn_training.ipynb`, `ml/lstm/models/lstm_v1.h5`, `ml/lstm/models/scaler.pkl`, and `ml/lstm/notebooks/01_lstm_training.ipynb`. Extend `.gitignore` to cover notebooks generally via `*.ipynb`.
- Baseline impact: No baseline revision. The three governing docs do not define git artifact-tracking policy; this is repository hygiene to prevent large or credential-prone local artifacts from continuing to be tracked.
- Evidence: `git rm --cached` removed only the four listed files from the index; `Test-Path` confirmed local copies remain; `git check-ignore -v` confirmed `.h5`, `.pkl`, and `.ipynb` rules now cover them.
- Approved by: Project owner
- Affected files/components: `.gitignore`, the four listed legacy model/notebook artifacts.

### OTD-017: Revert Of Unapproved LSTM API Wiring

- Date: 2026-05-29
- Classification: Supporting implementation
- Decision: Commit `cb6c0c9b` ("wire tracker lstm inference behind explicit sequence") was reverted by commit `b5e2d5f1` because the LSTM API wiring was not approved before it was implemented and pushed. The active approved position is: (1) the tracker-aligned 720×8 LSTM candidate artifact is accepted and documented under OTD-016; (2) API wiring of the new model remains pending and requires explicit approval; (3) the existing fallback behaviour remains active; (4) Platt calibration is baseline-required but implementation decisions remain unresolved. No production readiness is claimed. No calibrated Monte Carlo integration with the new LSTM output exists.
- Baseline impact: No baseline revision. Restores the branch to the last approved state (safe documentation only). The unapproved commit is preserved on local branch `backup/unapproved-lstm-wiring-cb6c0c9b` for future reference.
- Evidence: `git revert cb6c0c9b` executed cleanly; revert commit `b5e2d5f1` pushed to `origin/feat/event-hardening` on 2026-05-29.
- Approved by: Project owner (directed the revert)
- Affected files/components: `api/routers/predict.py` (restored to pre-wiring state), `api/tests/test_predict_tracker_contract.py` (removed; was introduced by the unapproved commit).

### OTD-016: Tracker-Aligned LSTM Candidate Artifact Accepted

- Date: 2026-05-29
- Classification: Supporting implementation
- Decision: The tracker-aligned 720x8 model is accepted as the current candidate artifact. The fitted scaler has been recreated to support it. The synthetic-data limitation and overlapping-window evaluation caveat are documented. The existing API fallback model remains active until safe wiring of the new 720x8 model is explicitly approved and implemented.
- Baseline impact: No baseline revision. Resolves the configuration conflict (OTD-006) by selecting the tracker specification.
- Evidence: Metadata JSON confirms `test_auc_roc: 0.9857` and scaler transformation verified.
- Approved by: Project owner
- Affected files/components: `ml/lstm/models/tracker_720x8/`, LSTM checklist items.

### OTD-015: Timeline Dates Are Planning Context; Product Requirements Are Hard

- Date: 2026-05-29
- Classification: Baseline interpretation
- Decision: The dates, sprint timing, and original delivery calendar in the three controlling documents are treated as planning context, not as hard enforcement constraints, because OTDT has already been built faster than the original timeline. Product behaviour requirements remain hard requirements: the 90-day maintenance schedule (a product feature), WP-07 demo values, five-agent scope, Unity XR plus Three.js demo experience, top-five Maximo work-order story, and all acceptance targets are not relaxed by this timeline reinterpretation. Acceptance targets may only be revised by an explicit project-owner decision recorded in this log.
- Baseline impact: No baseline revision. This clarifies interpretation of schedule artifacts without changing any product requirement, demo value, agent scope, or acceptance target.
- Evidence: Project-owner instruction on 2026-05-29; OTDT delivery progress already exceeds original timeline assumptions.
- Approved by: Project owner
- Affected files/components: `docs/product_baseline.md` (new "Timeline Interpretation" section), `docs/Decision Log.md` (this entry), `docs/Implementation Checklist.md` (work log entry).

### OTD-014: Unity What-If API Contract Fixed

- Date: 2026-05-29
- Classification: Baseline implementation
- Decision: The calibrated What-If demo route (`POST /api/monte-carlo/whatif`) now accepts both the Unity payload shape (`{ asset_id, deferral_days }`) and the existing date shape (`{ asset_id, maintenance_date }`). This resolves the contract mismatch that prevented Unity's `WhatIfSlider.cs` from reliably producing baseline demo values.
- Baseline impact: No baseline revision. The calibrated demo behaviour is preserved: `deferral_days=0` returns 34%, `deferral_days=45` returns 68% / USD 122,400. The stochastic engine-backed route at `/whatif/simulate` is unchanged and remains a separate path.
- Evidence: Function-level verification (18/18 checks passed) and HTTP-boundary ASGI transport verification (22/22 checks passed) on 2026-05-29. Unity `WhatIfSlider.cs` sends `{ asset_id, deferral_days }` which now matches the API contract.
- Approved by: Project owner (requested in Step 1/Step 2 task instructions)
- Affected files/components: `api/routers/monte_carlo.py`, `api/tests/test_whatif_contract.py` (new), `api/tests/verify_whatif.py` (new), `api/tests/verify_whatif_http.py` (new).
- Remaining scope: Unity Editor play-mode What-If slider verified on 2026-05-29 (0d=34%, 45d=68%/$122,400, 112d=83.9%/$150,984). The stochastic engine route (`/whatif/simulate`) still returns ~56% at 45 days and is not aligned with the calibrated demo — this remains open under OTD-009's original scope note.

### OTD-013: Root Baseline Artifact Set Confirmed

- Date: 2026-05-28
- Classification: Baseline interpretation
- Decision: The root DOCX, PPTX, and XLSX control OTDT delivery. Older generated docs are historical/supporting.
- Baseline impact: Establishes `OT_Digital_Twin_Build_Guide.docx`, `OT_Digital_Twin_Build_Deck.pptx`, and `OT_Digital_Twin_MVP_Tracker.xlsx` as the active source of truth.
- Evidence: Project owner instruction on 2026-05-28.
- Approved by: Project owner
- Affected files/components: All documentation, repository governance.

### OTD-008: IBM Integration And Cloud Training Work Paused

- Date: 2026-05-26
- Classification: Supporting implementation
- Decision: Active IBM Cloud / TechZone / Watson Studio / watsonx work and related cloud-training or IBM-integration execution are paused pending project-owner reactivation because the provisioned environment currently does not allow creating the required Studio project. This pause also applies to active Maximo, OpenShift, Watson IoT, Event Streams and API Connect integration work.
- Baseline impact: No baseline revision. The IBM platform elements and the original LSTM/Monte Carlo workflow remain part of the three-source OTDT baseline and must not be removed, downgraded or replaced solely because execution is paused.
- Evidence: Project-owner instruction on 2026-05-26 after the IBM Cloud project-creation blocker.
- Approved by: Project owner
- Affected files/components: TechZone/watsonx/Watson Studio validation or training, IBM platform integrations, cloud credentials/configuration and the draft retraining notebook.
- Resume condition: Project owner confirms that access/project creation is resolved or explicitly directs a new IBM integration attempt.

### OTD-007: Three Original Documents Control OTDT

- Date: 2026-05-26
- Classification: Baseline interpretation
- Decision: OTDT must be implemented and described according to the three original source documents identified by the project owner: `OT_Digital_Twin_Build_Guide.docx`, `OT_Digital_Twin_Build_Guide- pdf.pdf`, and `OT_Digital_Twin_MVP_Tracker.xlsx`. They govern product intent, data usage, model workflow and required behaviour.
- Baseline impact: Confirms the controlling authority set. Other material may be retained as historical or supporting context, but cannot override these three sources.
- Evidence: Project-owner instruction on 2026-05-26; verified source file presence and readable DOCX/PDF provenance.
- Approved by: Project owner
- Affected files/components: All OTDT product documentation, training notebooks, model evaluation, simulation integration and future implementation work.

### OTD-005: Original Synthetic Historical Data Is Authoritative

- Date: 2026-05-26
- Classification: Baseline interpretation
- Decision: The synthetic historical data supplied in `OT_Digital_Twin_MVP_Tracker.xlsx` is the authoritative dataset package for OTDT. The baseline implementation workflow is to train the LSTM on the supplied historical sensor readings and use the supplied failure/validation history for the Monte Carlo risk simulation that supports the Unity WP-07 showcase.
- Baseline impact: This confirms the original data/model workflow; it does not revise the five-agent scope or official demo figures.
- Evidence: Project-owner clarification; `GDC_Assets`, `Sensor_Readings`, `Failure_History`, `MC_Validation`, and `AI_Model_Specs` tabs in the authoritative tracker.
- Approved by: Project owner
- Affected files/components: Data-loading, LSTM training/inference, Monte Carlo calibration/validation, Unity demo integration.

### OTD-004: Restore March Unity-Compatible Fallback Stream

- Date: 2026-05-26
- Classification: Baseline implementation
- Decision: Restore the `/twin/stream` mock/fallback payload to emit the five baseline sensor fields consumed by Unity: `temperature_c`, `pressure_bar`, `vibration_mm_s`, `flow_rate_kg_s`, and `rotation_rpm`.
- Baseline impact: Repairs a regression introduced after the March presentation; it does not revise the baseline data or demo narrative.
- Evidence: Commit comparison between `795122aa` (2026-03-30) and `d42e7cbe` (2026-05-19); Patch 3 diff and reported live fallback WebSocket verification for all 50 assets.
- Approved by: Project owner through requested restoration workflow
- Affected files/components: `api/main.py`, Unity `/twin/stream` consumer.
- Remaining scope: Kafka-cached telemetry and model/simulation sensor-contract alignment remain open under OTD-002 and OTD-003.

## Entry Template

Copy this block when a decision is approved:

```md
### OTD-XXX: Decision Title

- Date:
- Classification: Baseline interpretation | Supporting implementation | Proposed extension | Baseline revision
- Decision:
- Baseline impact:
- Evidence:
- Approved by:
- Affected files/components:
```
