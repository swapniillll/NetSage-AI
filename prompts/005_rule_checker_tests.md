# 005 — Rule Checker Unit Tests

## Context
TASK-004 is done: `scripts/rule_checker.py` exists with `run_all()` and 6 rule functions. Read that file to confirm exact function signatures before writing tests against it.

## Task
Write unit tests proving each of the 6 rules correctly triggers on a positive fixture and correctly does not trigger on a negative fixture.

## Files
Create: `tests/test_rule_checker.py`. Also produce `data/rule_results_sample.txt` (captured console output from running `run_all()` on a couple of real cases — required for the PS "sample output" deliverable).

## Requirements
- 2 synthetic `show_outputs` strings per rule (1 should trigger `True`, 1 should trigger `False`) = 12 test cases minimum.
- Test the specific `triggered` field only — don't over-assert on exact `detail` wording (that may reasonably vary).
- After tests pass, run `rule_checker.run_all()` on 2 real rows pulled from `data/cases.csv` and redirect/save that output to `data/rule_results_sample.txt`.

## Acceptance criteria
`pytest tests/test_rule_checker.py` — all 12+ tests pass. `data/rule_results_sample.txt` exists and contains readable findings for 2 real cases.

## Tests
This task's own test file, executed via `pytest tests/test_rule_checker.py -v`.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-005, log `tests/test_rule_checker.py` and `data/rule_results_sample.txt`.

## Git
Commit: `TASK-005: rule checker unit tests + sample output`
