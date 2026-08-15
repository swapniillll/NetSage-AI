# 003 — Case Dataset: Write 30 Cases

## Context
TASK-002 is done: `data/cases.csv` has a locked schema and 1 example row; `data/SCHEMA.md` documents it. Read `PROJECT_STATE.md` and `data/SCHEMA.md` before starting — do not invent new columns.

## Task
Append rows to `data/cases.csv` until it has ≥30 total rows (including the TASK-002 example), covering all 8 categories in this distribution: VLAN 5, Gateway/IP 5, DHCP 4, DNS 3, Routing 5, ACL 4, NAT 2, Wireless 2.

This task may be run across multiple sessions/context windows — e.g. "write the next 10 cases" — as long as each sub-run reads the current row count from `data/cases.csv` first and doesn't duplicate `case_id`s.

## Files
Edit only: `data/cases.csv` (append rows). Do not touch the header or any other file.

## Requirements
- Every `show_outputs` block must plausibly and specifically support its own `expected_fault` — write it the way a real Packet Tracer capture or lab note would read.
- `case_id`s must be unique (e.g. `C001`–`C030+`).
- Distribute severity realistically (not all "High").
- If a case is based on an actually-built Packet Tracer topology, note this honestly; do not claim simulated cases are real captures anywhere in the data or docs.

## Acceptance criteria
- `data/cases.csv` has ≥30 rows total.
- Category counts match the required distribution (or better).
- No duplicate `case_id`.
- Every row passes the TASK-002 schema tests.

## Tests
`pytest tests/test_schema.py` (must still pass for all rows) and `tests/test_dataset_coverage.py` — create this test: asserts row count ≥30, asserts each required category has at least its minimum count.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-003 only once the full 30+ rows exist; log the row count reached in "Files Produced Log". If stopping mid-batch, log progress under "In Progress" (e.g. "18/30 cases written, VLAN/Gateway/DHCP done, Routing/ACL/NAT/Wireless remaining") instead of checking the box.

## Git
Commit per meaningful batch: `TASK-003: add N cases (categories: ...)`; final commit when ≥30 reached: `TASK-003: complete — 30+ cases across all categories`
