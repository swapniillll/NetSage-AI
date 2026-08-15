# 008 — JSON Schema Validation & Retry Logic

## Context
TASK-007 (`scripts/diagnose.py`) exists and produces raw LLM output saved to `data/diagnoses.json`. Read `scripts/diagnose.py` to see exactly where the LLM response is parsed, so this task can hook in at the right point.

## Task
Add strict schema validation with a single retry on failure, and a safe fallback flag for anything still invalid, so the pipeline never crashes on a bad LLM response.

## Files
Create: `scripts/validate_diagnosis.py`. Edit: `scripts/diagnose.py` (call the new validator instead of trusting raw JSON directly).

## Requirements
- `jsonschema`-based schema matching TASK-006's contract exactly (`root_cause` str, `confidence` float 0–1, `osi_layer` str, `evidence` array of str, `next_command` str, `fix_steps` array of str).
- `validate(raw_response: str) -> dict` — parses and validates; on failure, returns a clear validation error object, does not raise.
- In `diagnose.py`: on first validation failure, retry the LLM call once with an added instruction ("your last response was invalid JSON — return only valid JSON matching the schema"). If it fails a second time, write `{"case_id": ..., "status": "needs_manual_review", "raw_response": ...}` instead of a normal diagnosis record — and log this to `PROJECT_STATE.md`'s "Known Issues" section so it isn't silently lost.

## Acceptance criteria
Feeding a deliberately malformed JSON string through `validate_diagnosis.py` returns a validation-error object, not an exception. A full run never crashes due to a single bad LLM response.

## Tests
Create `tests/test_validate_diagnosis.py` — 1 valid sample passes cleanly, 1 malformed sample is caught and correctly flagged.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-008, log `scripts/validate_diagnosis.py`, note any `needs_manual_review` flags that show up during smoke testing under "Known Issues."

## Git
Commit: `TASK-008: JSON schema validation + single-retry fallback`
