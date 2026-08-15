# 007 — AI Diagnosis Script

## Context
TASK-004 (`scripts/rule_checker.py`) and TASK-006 (`prompts_ai/diagnose_prompt.md`) are both done. Read both files to confirm the `Finding` shape and the prompt's placeholder names before writing this script.

## Task
Write the script that, per case, runs the rule checker, fills the prompt template, calls the LLM, and saves the raw + parsed diagnosis.

## Files
Create: `scripts/diagnose.py`. Do not modify `rule_checker.py` or `diagnose_prompt.md` in this task.

## Requirements
- Load `data/cases.csv`, for each row: run `rule_checker.run_all(show_outputs)`, fill `diagnose_prompt.md` placeholders with the case's fields + rule findings, call the LLM API (key read from `.env`, never hardcoded).
- Save each result to `data/diagnoses.json` as a dict keyed by `case_id`, containing the raw response, the parsed JSON fields, plus `prompt_version` (e.g. `"v1"`, matching the prompt file) and `model` (the model string used).
- Must be runnable on a single case (for testing) or the full dataset (`--all` flag or similar) — TASK-009 will call the full-dataset path.
- Do not add retry/validation logic here — that's TASK-008's job; this script should call into `validate_diagnosis.py` once it exists, but for now it's fine to save the raw parsed JSON directly.

## Acceptance criteria
Running the script on 3 sample cases produces 3 correctly-keyed entries in `data/diagnoses.json` matching the TASK-006 schema.

## Tests
Create `tests/test_diagnose_smoke.py` — mock the LLM API call (do not make real network calls in tests), assert the saved record has the correct keys and shape.

## Expected output
`scripts/diagnose.py`, a partial `data/diagnoses.json` with 3 entries for manual review before the full run in TASK-009.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-007, log `scripts/diagnose.py` and note "diagnoses.json has 3 sample entries only, full run happens in TASK-009."

## Git
Commit: `TASK-007: AI diagnosis script (sample run on 3 cases)`
