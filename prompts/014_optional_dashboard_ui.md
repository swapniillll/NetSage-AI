# 014 — Optional Static Dashboard UI (P2 — polish only)

## Context
P0 sequence (TASK-001 through TASK-013) is complete and the project is already submittable without this task. TASK-011's `dashboard/dashboard_data.json` exists with real metrics. This task is only started if there is real time left — check `PROJECT_STATE.md` and confirm TASK-013 is checked off first.

## Task
Build a single static HTML page for visual demo polish — no build step, no server, no backend logic.

## Files
Create: `dashboard/index.html` (inline CSS/JS, or a small `dashboard/app.js`/`dashboard/style.css` alongside it — keep it to at most 3 files total).

## Requirements
- Reads `dashboard/dashboard_data.json`, `data/diagnoses.json`, and `data/cases.csv` (or a single pre-baked combined JSON generated as a small addition to `build_dashboard.py`) client-side via `fetch`.
- Sections: the two charts already computed in TASK-011 (rendered via Chart.js from CDN, using the *same numbers*, not recalculated differently), a browsable case table (id, category, severity, AI verdict, review decision), and a simple click-through case detail view (evidence + AI JSON + review decision).
- No routing framework, no authentication, no backend service, no build tooling. Must open correctly via a plain `file://` path or a one-line static server (`python -m http.server`).

## Acceptance criteria
Numbers shown in the page exactly match `dashboard/dashboard_data.json`. Page works with zero build step.

## Tests
Manual visual check only — open the file, confirm charts render and case click-through works for at least 3 cases.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-014, log `dashboard/index.html` (+ any accompanying files).

## Git
Commit: `TASK-014: optional static dashboard UI (polish)`
