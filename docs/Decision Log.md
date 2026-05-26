# Product Decision Log: OT Digital Twin

## How To Use This Log

This log records decisions that interpret, extend, or revise the authoritative
baseline in `docs/Product Baseline.md`.

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
| OTD-001 | `Sensor_Readings` size is described as 43,800 records, while the source workbook contains 87,600 data rows. | Original PDF guide and workbook labels versus physical workbook row count checked on 2026-05-26. | Open: owner confirmation required before client-facing use. |
| OTD-002 | Mixed sensor schemas across codebase. The baseline workbook `Sensor_Readings` sheet uses columns `temperature_c`, `pressure_bar`, `vibration_mm_s`, `flow_rate_kg_s`, `rotation_rpm`, `health_score`, `failure_label`, `failure_event`. Verified legacy-key consumers include `sensor_simulator/config.py`, `sensor_simulator/simulator.py`, `sensor_simulator/kafka_publisher.py`, `api/routers/agent.py`, and `api/routers/predict.py`, which use turbine/bearing-specific names such as `bearing_temp_c`, `bearing_vibration_mms`, `steam_inlet_pressure_bar`, `turbine_rpm`, and `steam_flow_kgs`. In contrast, `api/routers/twin.py` already uses baseline-style sensor keys. | Workbook `Sensor_Readings` column headers versus current code sensor key names, inspected 2026-05-26. | Open: contract migration required before claiming full sensor-schema baseline alignment. Do not resolve by editing code without a coordinated migration plan. |
| OTD-003 | Sensor meaning and calibration are not aligned across current runtime code. The authoritative original tracker supplies separate datasets for different stages: `GDC_Assets` includes all 50 assets and WP-007; `Sensor_Readings` is the LSTM historical training sample and does not contain WP-007 readings; `Failure_History` includes all 50 assets and 11 WP-007 events; `MC_Validation` includes 7 WP-007 cases. The repository also contains a locally generated sensor workbook and runtime mock/calibration values that must not override the original tracker. | Original tracker inspection, repository comparison, March git history, and project-owner clarification on 2026-05-26. | Open engineering issue: align runtime schemas and calibrations to the authoritative workflow without treating the WP-007 demo or original historical data as erroneous. |
| OTD-006 | The original build guide and companion tracker specify different LSTM configurations. PDF Step 4 requires 7-day and 30-day rolling statistics per sensor, rate of change, cross-sensor correlations, equipment age, maintenance-event flag and a 20% holdout evaluation. The tracker `AI_Model_Specs` tab specifies a `720 x 8` input feature model (`temperature_c`, `pressure_bar`, `vibration_mm_s`, `flow_rate_kg_s`, `rotation_rpm`, `health_score`, `rolling_7d_temp_mean`, `rate_of_change_vibration`), failure weight x8, 100 epochs with patience 10, and 70/15/15 time split. | Original PDF pages 8 and 15-17 versus original workbook `AI_Model_Specs`, inspected 2026-05-26. | Open: project owner must select the controlling LSTM run specification, or approve running both as separately labelled source-faithful experiments. Do not present an unapproved hybrid notebook as baseline-compliant. |
| OTD-009 | The two runnable What-If paths do not produce the same original showcase result. `api/routers/monte_carlo.py` retains an explicit demo calibration of 34% at zero deferral and 68% at 45 days, while `api/routers/whatif.py` delegates to the Weibull engine and returned approximately 56% at 45 days during local verification. | Local execution on 2026-05-26: calibrated route produced 68% / USD 122,400 for 45 days; engine-backed route produced approximately 56% / USD 100,818 in that run. | Open: keep the demonstrated calibrated route for the original showcase; do not claim the separate engine-backed path is baseline-calibrated until model/simulation reconciliation is approved. |
| OTD-010 | The current scheduler validation does not reproduce the original priority-work-order story. After correcting its stale project path, the script executed against the repository asset dataset and scheduled all 50 assets as critical, rather than identifying three high-risk assets outside the calendar plan. | Local execution of `scheduler/test_scheduler.py` on 2026-05-26 after path repair. | Open: scheduler/calibration validation is required before presenting prioritisation output as aligned with the original showcase. |

## Approved Decisions

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
