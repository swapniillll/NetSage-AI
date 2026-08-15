# 004 — Python Rule Checker Core

## Context
TASK-002/003 done: `data/cases.csv` schema is locked (in-progress or complete dataset exists — this task doesn't need the full 30 to be finished, just the schema). Read `data/SCHEMA.md` for the `show_outputs` format before writing regexes.

## Task
Implement the 6 deterministic rule checks required by the PS: duplicate IP, wrong subnet mask, gateway mismatch, interface down, missing VLAN, missing route.

## Files
Create: `scripts/rule_checker.py`. Do not touch `data/` or other scripts.

## Requirements
- Functions: `check_duplicate_ip(show_outputs: str) -> Finding`, `check_wrong_mask(show_outputs: str) -> Finding`, `check_gateway_mismatch(show_outputs: str) -> Finding`, `check_interface_down(show_outputs: str) -> Finding`, `check_missing_vlan(show_outputs: str) -> Finding`, `check_missing_route(show_outputs: str) -> Finding`.
- `Finding` = a dict/dataclass with `rule_name: str, triggered: bool, detail: str`.
- `run_all(show_outputs: str) -> list[Finding]` calls all 6 and returns the list.
- Use regex/string matching against realistic `show` command patterns (e.g. `Vlan10 is down`, `ip address 10.0.0.5 255.255.255.0`, duplicate IP appearing twice across interfaces). This is a deliberate simplification vs. a full CLI parser — do not attempt to build a general Cisco config parser.
- Pure functions, no file I/O, no network calls, no external state — must be safely importable and unit-testable in isolation.

## Acceptance criteria
- `run_all()` returns exactly 6 `Finding` entries for any well-formed input string.
- Running `run_all()` against every `show_outputs` value currently in `data/cases.csv` completes with no exceptions.

## Tests
None written in this task — TASK-005 owns the test file. Do a manual smoke check only: run `run_all()` on 2–3 real rows from `cases.csv` and eyeball the output.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-004, log `scripts/rule_checker.py`.

## Git
Commit: `TASK-004: implement 6 deterministic rule checks`
