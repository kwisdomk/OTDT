# OTDT Agent Instructions

## Required Read

Before planning, writing, reviewing, or changing OTDT product behaviour or
documentation, read `docs/product_baseline.md`, `docs/Decision Log.md` and
`docs/Implementation Checklist.md`.

## Source Of Truth

The active source of truth is exclusively the following three root files:
1. `OT_Digital_Twin_Build_Guide.docx`
2. `OT_Digital_Twin_Build_Deck.pptx`
3. `OT_Digital_Twin_MVP_Tracker.xlsx`

These files are the mandatory controlling authority for intended product scope,
data usage, model workflow and demo facts. Later documents, generated reports,
existing README prose, and current code are not allowed to redefine the product
silently. If the three controlling files conflict with each other, record the
conflict and obtain project-owner direction before implementing a chosen
interpretation.

## Working Rules

- The product goal is the GDC Kenya OT Digital Twin MVP.
- Required agents are:
  - LSTM Failure Predictor
  - Monte Carlo Simulation Engine
  - Maintenance Scheduler
  - CNN Anomaly AI, with rule-based fallback allowed for MVP
  - What-If Analyst
- Primary demo flow is:
  - 50 GDC assets
  - Unity XR plus Three.js visualization
  - WP-07 / GDC-WP-007 demo asset
  - 34% 30-day failure probability
  - 45-day maintenance deferral
  - 68% deferred failure probability
  - USD 180,000 replacement/failure cost
  - USD 122,400 expected failure cost
  - USD 8,000 inspection cost
  - 90-day maintenance schedule
  - top-five Maximo work orders
  - 650% annual ROI story
- Do not present implemented, tested, deployed, or production-ready status
  without verifying it from the current repository or environment.
- Treat additional infrastructure and UI components as implementation choices
  unless the baseline explicitly requires them.
- Flag any conflict with baseline facts before making a product-level change.
- Do not inherit factual claims from `bob_/`, `implementation_plan.md`, project
  bibles, speedrun reports, or technical briefings without validation.
- Preserve unresolved ambiguity about `Sensor_Readings` row count unless the
  project owner records a decision.
- IBM integration and cloud-training execution are paused under `OTD-008`
  until the project owner reactivates them. Preserve them as baseline
  requirements; do not remove them or claim successful IBM execution.
- Maintain `docs/Implementation Checklist.md` as the living progress record.
  Tick items only with stated evidence and record the verification time in
  EAT; code presence alone does not prove original acceptance criteria.
- Record approved extensions, baseline interpretations, or baseline revisions
  in `docs/Decision Log.md`.

## Change Classification

For product-facing changes, state one of:

- `Baseline implementation`: implements an original required capability.
- `Supporting implementation`: helps deliver the baseline without changing it.
- `Proposed extension`: adds capability not specified in the baseline.
- `Baseline revision`: changes an authoritative product fact and requires
  explicit owner approval.
