# 002 — Data Schema & cases.csv Template

## Context
TASK-001 is done: repo scaffold + `PROJECT_STATE.md` exist. `data/` directory is empty. Read `PROJECT_STATE.md` before starting to confirm TASK-001 is checked off.

## Task
Define and lock the exact `cases.csv` column schema. This file is the source-of-truth contract every later task depends on — do not change it after this task without updating every downstream script.

## Files
Create: `data/cases.csv` (header row + exactly 1 fully filled example row), `data/SCHEMA.md`, `tests/test_schema.py`.

## Requirements
- Columns (exact names, exact order): `case_id, title, category, symptom, topology_note, show_outputs, expected_fault, osi_layer, concept, severity, expected_next_command, expected_fix`.
- `category` allowed values: `VLAN, Gateway/IP, DHCP, DNS, Routing, ACL, NAT, Wireless`.
- `show_outputs` is one CSV cell containing multi-line text (use `\n` escapes or quoted multi-line CSV fields) representing realistic Cisco `show` command output.
- `SCHEMA.md` documents each column: type, format, example, and the allowed `category` list.
- The one example row must be fully realistic and internally consistent (its `show_outputs` should actually support its `expected_fault`).

## Acceptance criteria
- `pandas.read_csv('data/cases.csv')` loads without error and returns exactly the 12 expected columns in order.
- The example row's `category` is a valid value.

## Tests
`pytest tests/test_schema.py` — asserts column names/order match exactly, asserts `category` is in the allowed set for every row present.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-002, log `data/cases.csv`, `data/SCHEMA.md`, `tests/test_schema.py` as produced.

## Git
Commit: `TASK-002: lock cases.csv schema`
