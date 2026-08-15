# 010 — Human Review Workflow

## Context
TASK-009 done: full `data/diagnoses.json` exists for every case. Read a handful of entries first to understand what a reviewer will actually be judging.

## Task
Produce the reviewer decision log — Accepted / Edited / Rejected + reason — for every case, including ≥5 genuine corrections.

## Files
Create: `scripts/review_cli.py` (optional convenience tool), `data/review_log.csv`.

## Requirements
- `review_log.csv` columns: `case_id, decision, corrected_fields, reason, reviewer`. `decision` ∈ {`Accepted`, `Edited`, `Rejected`}.
- `review_cli.py` (if built): prints one case's symptom/evidence/AI diagnosis, prompts for a decision + reason, appends to the CSV. This is optional — reviewing directly in a spreadsheet against the same column schema is equally acceptable and should not block this task.
- Every `case_id` from `cases.csv` must appear exactly once in `review_log.csv`.
- ≥5 rows must be `Edited` or `Rejected` with a genuine, specific `reason` (not fabricated) — pick cases where the AI plausibly under-performed (ambiguous symptom, sparse evidence, wrong next_command, missed rule-checker finding).

## Acceptance criteria
`review_log.csv` row count equals `cases.csv` row count; ≥5 rows are Edited/Rejected with non-empty, specific reasons.

## Tests
Create `tests/test_review_log.py` — asserts row count matches, asserts ≥5 correction rows exist, asserts every `case_id` in `cases.csv` has a matching row.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-010, log `data/review_log.csv` (and `scripts/review_cli.py` if built).

## Git
Commit: `TASK-010: human review log (Accept/Edit/Reject for all cases)`
