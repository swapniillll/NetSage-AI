# 009 — Pipeline Integration: Run All Cases

## Context
TASK-003 (30+ cases), TASK-005 (rule checker tested), TASK-008 (validated diagnosis) should all be done. Read `PROJECT_STATE.md` and confirm all three are checked off before starting — this task requires the full dataset to be meaningful.

## Task
Wire everything into one command that runs the entire pipeline from `cases.csv` to a complete `diagnoses.json` and `rule_results.json`.

## Files
Create: `scripts/run_pipeline.py`. This should orchestrate (import and call) `rule_checker.py`, `diagnose.py`, and `validate_diagnosis.py` — do not duplicate their logic here.

## Requirements
- Single entrypoint: `python scripts/run_pipeline.py` processes every row in `data/cases.csv`.
- Saves full `data/diagnoses.json` (all cases) and full `data/rule_results.json` (all cases, all 6 rules each).
- Prints per-case progress to console (`case_id: done` / `case_id: needs_manual_review`).
- Must not crash on any single case failure — log and continue (this is what TASK-008's fallback exists for).

## Acceptance criteria
Running the script against the full 30+-case dataset completes without crashing, and produces a diagnosis or an explicit `needs_manual_review` flag for every case.

## Tests
Create `tests/test_pipeline_integration.py` — run the orchestrator against a 5-case subset (can slice `cases.csv` in the test), assert both output files are created and every one of the 5 cases has an entry.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-009, log `scripts/run_pipeline.py`, `data/diagnoses.json` (full), `data/rule_results.json` (full). List any `needs_manual_review` case IDs under "Known Issues."

## Git
Commit: `TASK-009: full pipeline run across all cases`
