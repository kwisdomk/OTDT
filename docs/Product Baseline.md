# Product Baseline: OT Digital Twin

## Purpose

This document prevents product drift while OTDT is implemented with human and AI
contributors. It defines the authoritative product intent supplied for the
original March 2026 showcase. Code may implement that intent, but it must not
silently redefine it.

## Authority

The following three original artifacts are the mandatory controlling definition
of what OTDT was intended to become and how it must work:

1. `Q:\ibm\EAAAIW @ IBM Research Lab Africa\AGENTIC AI Projects\OT_Digital_Twin_Build_Guide.docx`
2. `Q:\ibm\EAAAIW @ IBM Research Lab Africa\AGENTIC AI Projects\OT_Digital_Twin_Build_Guide- pdf.pdf`
3. `Q:\ibm\EAAAIW @ IBM Research Lab Africa\AGENTIC AI Projects\OT_Digital_Twin_MVP_Tracker.xlsx`

The repository copy at `docs/architecture/OT_Digital_Twin_Build_Guide.docx`
is byte-identical to the authoritative DOCX as checked on 2026-05-26.

These three sources must be followed for product intent, data usage, model
workflow, original MVP requirements and demo facts. Where they conflict with
each other or omit information needed for implementation, the conflict must be
recorded and resolved by the project owner; no AI-generated assumption may
silently fill the gap.

These sources do not
prove that any feature has been implemented, tested, deployed, or accepted.
Implementation status must be established from current code, tests, deployed
systems, or user confirmation.

## Locked Product Intent

Unless the project owner explicitly approves a change, OTDT must continue to
represent the following product:

| Topic | Baseline requirement |
| --- | --- |
| Product | OT Digital Twin, Solution 04 of 08 in the i3 East Africa Agentic AI Platform |
| Purpose | Probabilistic predictive maintenance through a digital twin of industrial equipment |
| MVP client/context | GDC Kenya geothermal plant demonstration |
| Data truth | MVP data is synthetic; never present it as live client operational data |
| Asset model | 50 GDC assets: 20 well pumps, 10 heat exchangers, 10 turbines, 10 production pipes |
| Demonstration asset | Well Pump `GDC-WP-007` / WP-07 |
| Visual experience | Unity XR primary visualisation plus Three.js browser viewer |
| IBM/platform elements named in baseline | Maximo MAS 9.1 APM, Watson Studio ML Lab, watsonx.ai, Watson IoT Platform, Event Streams/Kafka, OpenShift, API Connect |
| API element named in baseline | FastAPI sensor and simulation service layer |

## Five Agents

The baseline agents are:

1. **Failure Predictor**: LSTM model producing failure probability curves over
   30/60/90-day windows.
2. **Monte Carlo Simulation Engine**: 10,000 probabilistic failure scenarios
   based on asset condition and failure distributions.
3. **Maintenance Scheduler**: optimised inspection schedules and priority work
   order output.
4. **Anomaly AI**: CNN visual anomaly detection in the digital twin.
5. **What-If Analyst**: interactive maintenance deferral analysis.

Do not replace this agent set with an invented agent taxonomy. An implementation
may add supporting services, but they must be described as services or approved
extensions, not as original baseline agents.

## Authoritative Data And Model Workflow

The original tracker is the authoritative synthetic data package for the
baseline implementation. Its tabs play different roles and must not be
conflated:

| Tracker tab | Baseline role | Verified coverage |
| --- | --- | --- |
| `GDC_Assets` | Asset inventory for the digital twin / Maximo loading | 50 assets, including `GDC-WP-007` |
| `Sensor_Readings` | Historical time-series training input for the LSTM failure predictor | 10 representative assets; no WP-007 time-series row in the supplied tab |
| `Failure_History` | Historical failure-event input for Weibull fitting | 500 events across all 50 assets; includes WP-007 |
| `MC_Validation` | Historical cases for Monte Carlo validation | Well-pump validation cases; includes WP-007 |

The intended pipeline is:

1. Train the LSTM failure predictor on the supplied historical sensor data.
2. Fit and validate the Monte Carlo simulation using the supplied failure and
   validation history.
3. Use the resulting risk outputs in the WP-07 Unity/what-if demonstration.

The absence of WP-07 from the `Sensor_Readings` training sample does not remove
WP-07 from the baseline product or demo. It is present in the asset inventory,
failure history and Monte Carlo validation data.

## Official Demo Narrative

The intended showcase story is fixed unless the owner approves a revision:

1. Failure prediction: WP-07 has a 34% probability of failure within 30 days
   while its calendar inspection is still 45 days away.
2. What-if analysis: deferring maintenance by 45 days increases failure
   probability from 34% to 68%.
3. Expected-cost explanation: a USD 180,000 unplanned failure at 68% risk gives
   an expected failure cost of USD 122,400, compared with USD 8,000 inspection
   cost.
4. Optimised schedule: highlight three assets outside the current calendar plan
   with greater than 30% 30-day risk and create priority Maximo work orders.
5. Annual ROI narrative: two avoided failures produce USD 360,000 savings
   against USD 48,000 annual platform cost, yielding 650% ROI.

## Original MVP Targets

| Metric | Baseline target |
| --- | --- |
| LSTM failure predictor | Greater than 82% AUC-ROC on 30-day holdout |
| Monte Carlo speed | 10,000 scenarios in less than 5 seconds |
| What-If response | Less than 2 seconds |
| 3D sensor update latency | Less than 1 second |
| Anomaly detection | Greater than 80% on synthetic visual anomaly set |
| Demonstration milestone | Live Monte Carlo decision scenario for GDC Kenya audience |

## Known Baseline Ambiguity

The original build guide and tracker materials disagree with the physical size
of `Sensor_Readings`:

- The original PDF and workbook descriptive labels state 43,800 records.
- Reading the workbook on 2026-05-26 found 87,600 data rows in the
  `Sensor_Readings` worksheet.

Do not quietly choose one figure in client-facing materials or model-validation
claims. Treat this as an unresolved baseline inconsistency until the project
owner confirms the intended dataset interpretation.

## Implementation Versus Baseline

Implementation decisions are allowed when they support the locked product
intent and are accurately labelled. For example, Redis caching, TimescaleDB
storage, WebSocket streaming, React dashboards, local Docker workflows, mock
clients, CI pipelines, and test harnesses may be valid engineering choices.
They are not automatically source-specified requirements merely because later
documents or code contain them.

When adding or retaining such a choice:

- Describe it as an implementation decision or demo support capability.
- Do not claim it was in the original baseline unless one of the three authority
  artifacts supports the claim.
- Do not change locked product facts to suit the implementation.

## Current Delivery Hold

As directed by the project owner on 2026-05-26, active IBM platform integration
and cloud-model execution are paused pending renewed approval after a Watson
Studio project-creation blocker. This hold includes TechZone/watsonx/Watson
Studio training and active Maximo, OpenShift, Watson IoT, Event Streams or API
Connect integration work.

This pause does not remove IBM platform elements from the original baseline.
Local code recovery must preserve the future integration boundaries, must not
claim live IBM execution, and must not execute a draft retraining notebook or
present it as the original March model history while the hold remains active.

## Non-Authoritative Material

The repository contains derivative planning, briefing, generated, status and
implementation documents. These can contain useful context or code guidance,
but cannot override the baseline. This includes:

- `bob_/`
- `implementation_plan.md`
- `docs/architecture/speedrun2IEEE.docx`
- `docs/architecture/litttle_technical_info_OTDT.pdf`
- external `build guides/` and `docs/OT_Digital_Twin_Technical_Briefing.md`

Known conflicting derivative claims include a single turbine demo asset,
USD 8.2M / USD 150K / 54x ROI narratives, a three-component replacement for
the five-agent product, and later event/sprint scopes.

## Change Rule

Any requested change that affects product facts, demo numbers, assets, agents,
target client, datasets, named MVP features, or business claims must:

1. Be checked against this baseline and, where needed, the original artifact.
2. State whether it is baseline implementation, a proposed extension, or a
   deliberate baseline revision.
3. Obtain owner confirmation before implementing a contradiction or replacing
   a baseline requirement.
