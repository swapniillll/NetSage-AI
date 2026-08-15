# 012 — Responsible AI Log

## Context
TASK-010 done: `data/review_log.csv` has ≥5 Edited/Rejected rows with reasons. Read those rows plus their corresponding entries in `data/diagnoses.json` before writing this doc.

## Task
Write the narrative Responsible AI documentation the PS explicitly requires — notes on ≥5 corrected AI responses.

## Files
Create: `docs/responsible_ai_log.md`.

## Requirements
For each of the ≥5 corrected cases (pulled directly from `review_log.csv`), include: `case_id`; what the AI diagnosed (from `diagnoses.json`); what was actually wrong with it — classify as one of: incorrect root cause, insufficient evidence, low confidence, wrong `next_command`, or missed a rule-checker finding; the corrected/final diagnosis; a one-line "why this matters" note. Do not fabricate or embellish beyond what's actually in `review_log.csv`'s `reason` field.

## Acceptance criteria
≥5 complete entries, every referenced `case_id` exists in `cases.csv` and `review_log.csv`.

## Tests
Create `tests/test_responsible_ai_log.py` — parses the markdown for `case_id` mentions, asserts ≥5 distinct cases are covered and each exists in `review_log.csv`.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-012, log `docs/responsible_ai_log.md`.

## Git
Commit: `TASK-012: responsible AI log (5+ corrections documented)`
