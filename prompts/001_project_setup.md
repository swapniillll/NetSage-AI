# 001 — Project Setup

## Context
Empty/new repository. No prior files exist. This is the first task in the sequence.

## Task
Scaffold the repository structure and the `PROJECT_STATE.md` tracker that every subsequent task will read/update.

## Files
Create: `README.md`, `PROJECT_STATE.md`, `requirements.txt`, `.gitignore`, empty directories `data/`, `prompts_ai/`, `scripts/`, `tests/`, `dashboard/`, `docs/`.
Do not create any other files.

## Requirements
- `requirements.txt`: `pandas`, `pytest`, `jsonschema`, `matplotlib`, and an LLM SDK (e.g. `anthropic`).
- `.gitignore`: standard Python (`__pycache__/`, `.pytest_cache/`, `*.pyc`, `.env`).
- `README.md`: placeholder with project title and a "will be completed in TASK-015" note.
- `PROJECT_STATE.md`: use the template already provided in the plan pack — a checklist of TASK-001 through TASK-015, an "In Progress" section (empty), a "Files Produced Log" section (empty), a "Known Issues" section (empty).
- Do not add any API keys or secrets to any file. Use `.env` (git-ignored) for the LLM API key, referenced but not committed.

## Acceptance criteria
- `pip install -r requirements.txt` completes without error.
- Folder structure matches exactly what's listed above.
- `PROJECT_STATE.md` lists all 15 tasks as unchecked.

## Tests
None — structural task. Confirm folders exist via `ls -R`.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-001, log files produced, leave "In Progress" empty.

## Git
Commit: `TASK-001: project scaffold + state tracker`
