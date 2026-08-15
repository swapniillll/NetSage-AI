# 013 — Testing & PS Acceptance Checklist

## Context
TASK-001 through TASK-012 should all be checked off in `PROJECT_STATE.md`. This is the P0-sequence closing task — read `PROJECT_STATE.md` fully before starting to confirm nothing upstream is still "In Progress."

## Task
Run the complete test suite and produce a filled-in, evidence-linked PS acceptance checklist. This is the gate that confirms the project is genuinely Cisco-PS-compliant, not just "code exists."

## Files
Create: `docs/SUBMISSION_CHECKLIST.md`.

## Requirements
- Run `pytest` (full suite, every test file created in TASK-002 through TASK-012). All must pass — if something fails, fix the underlying issue in its owning task's files, don't patch around it here.
- `SUBMISSION_CHECKLIST.md` mirrors the 15-item list from the approved PRD (§19), each item checked off with a one-line pointer to where the evidence actually lives in the repo (e.g. "✅ ≥30 cases across all categories — see `data/cases.csv`, verified by `tests/test_dataset_coverage.py`").

## Acceptance criteria
`pytest` reports 0 failures across the whole repo. Every checklist item is checked with a real file reference, not a guess.

## Tests
`pytest` (entire suite, run from repo root).

## Documentation
Update `PROJECT_STATE.md`: check off TASK-013, log `docs/SUBMISSION_CHECKLIST.md`. Note the P0 sequence is now complete.

## Git
Commit: `TASK-013: full test pass + PS acceptance checklist — P0 sequence complete`
