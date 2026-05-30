# OTDT Documentation Index

This index classifies the OTDT documentation to clarify governance and source of truth.

## Explicit Rule

**Do not implement OTDT features from historical/supporting documents unless the requirement is confirmed against the active baseline.**

## Active Baseline

These three root files are the mandatory controlling authority and active source of truth for the OTDT product intent, scope, and facts:
1. `OT_Digital_Twin_Build_Guide.docx`
2. `OT_Digital_Twin_Build_Deck.pptx`
3. `OT_Digital_Twin_MVP_Tracker.xlsx`

## Active Governance

These files enforce the baseline and track implementation progress:
- `AGENTS.md`: Agent and contributor instructions.
- `docs/product_baseline.md`: Defines the authoritative product intent.
- `docs/Decision Log.md`: Records approved decisions, extensions, or revisions to the baseline.
- `docs/Implementation Checklist.md`: Tracks implementation progress against the baseline.
- `docs/documentation_index.md`: Classifies active, operational, project-management, and historical documentation.

## Project Management / Status Reports

- `docs/project_management/OTDT_Current_State_Assessment_2026-05-27.docx`
- `docs/project_management/OTDT_Baseline_Aligned_Delivery_Workplan_2026-05-27.docx`

## Operational Runbooks

These files explain how to run the current system locally. They are operational guidance, not product authority:
- `docs/runbooks/short_unity_demo_runbook.md`: Fast local Unity visual demo path.
- `docs/runbooks/long_engineering_smoke_test_runbook.md`: Broader current-state smoke test path.

## Historical / Supporting Material

All other documents, generated reports, architecture notes, and implementation plans are historical or supporting. They must not redefine the product silently. This includes:
- `bob_/` files
- `implementation_plan.md`
- Previous build guides or architecture notes
- Any other generated status reports or documentation not explicitly listed in the Active Baseline or Active Governance sections.
