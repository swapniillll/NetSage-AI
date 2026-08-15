# PROJECT_STATE.md
This file is the single source of truth for "what's actually built." Every task reads this first and updates it last. If a session ends unexpectedly, the next session trusts this file over any assumption.

## Task Checklist
- [x] TASK-001 — Project Setup & Repo Scaffold
- [x] TASK-002 — Data Schema & cases.csv Template
- [x] TASK-003 — Case Dataset: Write 30 Cases
- [x] TASK-004 — Python Rule Checker Core
- [x] TASK-005 — Rule Checker Unit Tests
- [ ] TASK-006 — AI Diagnosis Prompt Design
- [ ] TASK-007 — AI Diagnosis Script
- [ ] TASK-008 — JSON Schema Validation & Retry Logic
- [ ] TASK-009 — Pipeline Integration: Run All Cases
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

## Known Issues / Deferred Items
_(anything explicitly skipped or flagged needs_manual_review — list here so nothing is silently lost)_
