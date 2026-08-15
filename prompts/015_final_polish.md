# 015 — Final Polish: README, Docs, Submission Packaging

## Context
TASK-013 is complete (P0 done, checklist filled). TASK-014 may or may not be done — this task does not depend on it. Read `PROJECT_STATE.md` and `docs/SUBMISSION_CHECKLIST.md` before starting.

## Task
Finalize the README and package the repo so a stranger (or the demo video viewer) can understand and run the whole thing without prior context.

## Files
Edit: `README.md` (finalize the placeholder from TASK-001). Create: `docs/architecture_notes.md`. Reorganize/copy files as needed so PS-required deliverable names are present at the expected top-level locations (`cases.csv`, `diagnose_prompt.md`, the Python checker, the dashboard, the responsible AI log).

## Requirements
- README covers: one-paragraph project description; exact commands to run the full pipeline (`python scripts/run_pipeline.py`, then `python scripts/build_dashboard.py`); a file map showing where each PS deliverable lives; how to run tests (`pytest`); note on the intentional simplifications made (file-based pipeline instead of a web app/DB, regex-based rule checker instead of a full CLI parser) and why (per the approved PRD).
- `architecture_notes.md`: short version of the pipeline diagram from the PRD (`cases.csv → rule_checker → diagnose → review → dashboard`), one paragraph per stage.
- Do not change any technical content, logic, or data while doing this — this task is documentation and packaging only.

## Acceptance criteria
Following the README's own instructions from a clean checkout reproduces the pipeline successfully. All PS deliverable filenames are present and locatable exactly as named in the PS.

## Tests
Dry-run the README's instructions end-to-end from a clean clone/checkout.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-015, log `README.md` (finalized) and `docs/architecture_notes.md`.

## Git
Commit: `TASK-015: finalize README + docs + submission packaging`
