# 011 — Dashboard Metrics & Charts

## Context
TASK-009 (`data/diagnoses.json`, `data/rule_results.json`) and TASK-010 (`data/review_log.csv`) are both done. Read all three files' actual structure before writing the aggregation logic.

## Task
Compute every PS-required metric from real data and produce the chart deliverable. This alone satisfies the PS "Dashboard: spreadsheet or simple chart" requirement — no web UI is required for this task.

## Files
Create: `scripts/build_dashboard.py`, `dashboard/dashboard_data.json`, `dashboard/issue_distribution.png`, `dashboard/agreement_rate.png`.

## Requirements
- Metrics to compute, all from real files (no hardcoded numbers): total cases; issue-type distribution (count by `category`); severity distribution (count by `severity`); Accepted/Edited/Rejected counts; `agreement_rate = Accepted / Total`; `correction_rate = (Edited + Rejected) / Total`; rule-finding counts by rule name (from `rule_results.json`).
- Save all metrics to `dashboard/dashboard_data.json`.
- Save a bar chart (`issue_distribution.png`, category counts) and a pie/donut chart (`agreement_rate.png`, Accepted/Edited/Rejected split) via matplotlib.

## Acceptance criteria
Every number in `dashboard_data.json` matches an independent manual `pandas.groupby` check on the same source files.

## Tests
Create `tests/test_dashboard_metrics.py` — recompute `agreement_rate` and category counts independently inside the test and assert they match `dashboard_data.json`.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-011, log `scripts/build_dashboard.py`, `dashboard/dashboard_data.json`, and both PNGs.

## Git
Commit: `TASK-011: dashboard metrics + charts from real data`
