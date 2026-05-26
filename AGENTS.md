# OTDT Agent Instructions

## Required Read

Before planning, writing, reviewing, or changing OTDT product behaviour or
documentation, read `docs/Product Baseline.md`, `docs/Decision Log.md` and
`docs/Implementation Checklist.md`.

## Source Of Truth

The three original March 2026 files listed in `docs/Product Baseline.md` are
the mandatory controlling authority for intended product scope, data usage,
model workflow and demo facts. Later documents, generated reports, existing
README prose, and current code are not allowed to redefine the product
silently. If the three controlling files conflict with each other, record the
conflict and obtain project-owner direction before implementing a chosen
interpretation.

## Working Rules

- Preserve the baseline identity: GDC Kenya geothermal MVP, 50 modelled assets,
  demo asset `GDC-WP-007`, five baseline agents, synthetic MVP data, and the
  official WP-07/What-If/ROI scenario.
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
