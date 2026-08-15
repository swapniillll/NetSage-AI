# PROJECT_STATE.md
This file is the single source of truth for "what's actually built." Every task reads this first and updates it last. If a session ends unexpectedly, the next session trusts this file over any assumption.

## Task Checklist
- [x] TASK-001 — Project Setup & Repo Scaffold
- [x] TASK-002 — Data Schema & cases.csv Template
- [x] TASK-003 — Case Dataset: Write 30 Cases
- [x] TASK-004 — Python Rule Checker Core
- [x] TASK-005 — Rule Checker Unit Tests
- [x] TASK-006 — AI Diagnosis Prompt Design
- [x] TASK-007 — AI Diagnosis Script
- [x] TASK-008 — JSON Schema Validation & Retry Logic
- [x] TASK-009 — Pipeline Integration: Run All Cases
- [ ] TASK-010 — Human Review Workflow
- [ ] TASK-011 — Dashboard Metrics & Charts
- [ ] TASK-012 — Responsible AI Log
- [ ] TASK-013 — Testing & PS Acceptance Checklist
- [ ] TASK-015 — Final Polish (README/packaging) [P1]
- [ ] TASK-014 — Optional Static Dashboard UI [P2]

## In Progress (fill in only if a task was interrupted mid-way)
_none currently_

## Files Produced Log
_(append one line per task on completion: `TASK-0XX: file1, file2, ...`)_
TASK-001: README.md, PROJECT_STATE.md, requirements.txt, .gitignore
TASK-002: data/cases.csv, data/SCHEMA.md, tests/test_schema.py
TASK-003: data/cases.csv (30 rows: VLAN 5, Gateway/IP 5, DHCP 4, DNS 3, Routing 5, ACL 4, NAT 2, Wireless 2), tests/test_dataset_coverage.py
TASK-004: scripts/rule_checker.py
TASK-005: tests/test_rule_checker.py, data/rule_results_sample.txt
TASK-006: prompts_ai/diagnose_prompt.md
TASK-007: scripts/diagnose.py, tests/test_diagnose_smoke.py. (Note: diagnoses.json contains 0 real API-generated entries because the execution environment lacked ANTHROPIC_API_KEY; the mocked smoke test verified the 3-case pipeline. Full dataset run happens in TASK-009.)
TASK-008: scripts/validate_diagnosis.py, tests/test_validate_diagnosis.py
TASK-009: scripts/run_pipeline.py, tests/test_pipeline_integration.py. (Note: The real full dataset run is BLOCKED due to an unavailable ANTHROPIC_API_KEY credential. Output generation deferred).

## Known Issues / Deferred Items
_(anything explicitly skipped or flagged needs_manual_review — list here so nothing is silently lost)_
