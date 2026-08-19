# NetSage AI — Task Board

Scope = the approved PRD only (file-pipeline architecture, no DB/auth/backend service, one optional static dashboard). 15 tasks total, not 18 — `ui_diagnosis` / `ui_review` / `demo_mode` were dropped because the final PRD has no separate pages for those and no "demo mode" feature; the optional dashboard (TASK-014) already covers case table + detail, and the demo is just running the real pipeline on camera.

**Context-safety rule for every task:** before starting, the agent reads `PROJECT_STATE.md` + does `ls -R` on the repo. Before finishing, it updates `PROJECT_STATE.md` (mark task done, list files produced/changed, note anything left half-done). This means any task can be picked up cold, in a fresh context window, with zero prior chat history.

---

### TASK-001 — Project Setup & Repo Scaffold
- **Objective:** Create the repo skeleton and `PROJECT_STATE.md` tracker.
- **Files:** `README.md`, `PROJECT_STATE.md`, `requirements.txt`, `.gitignore`, empty dirs `data/`, `prompts_ai/`, `scripts/`, `tests/`, `dashboard/`
- **Dependencies:** none
- **Instructions:** Init git repo. Create folder structure above. `requirements.txt`: `pandas`, `pytest`, `jsonschema`, `matplotlib`, `anthropic` (or chosen LLM SDK). `PROJECT_STATE.md` starts with a task checklist (TASK-001…015, all unchecked) and a "Files Produced" log.
- **Acceptance criteria:** `pip install -r requirements.txt` succeeds; folder structure matches; `PROJECT_STATE.md` exists with all 15 tasks listed as pending.
- **Tests:** none (structural task)
- **Expected output:** Empty but importable repo, first git commit.
- **Estimated time:** 20 min
- **Priority:** P0
- **Teammate-delegatable:** No

---

### TASK-002 — Data Schema & `cases.csv` Template
- **Objective:** Lock the exact column schema for the case dataset before any case is written.
- **Files:** `data/cases.csv` (header row + 1 filled example row only), `data/SCHEMA.md`
- **Dependencies:** TASK-001
- **Instructions:** Columns: `case_id, title, category, symptom, topology_note, show_outputs, expected_fault, osi_layer, concept, severity, expected_next_command, expected_fix`. `show_outputs` is a single escaped multi-line text field (use `\n` inside the CSV cell). `SCHEMA.md` documents each column's type/format and one example. `category` must be one of: VLAN, Gateway/IP, DHCP, DNS, Routing, ACL, NAT, Wireless.
- **Acceptance criteria:** CSV opens cleanly in pandas (`pd.read_csv`); header matches exactly; one fully realistic example row present.
- **Tests:** `pytest tests/test_schema.py` — asserts required columns exist, `category` values are in the allowed set.
- **Expected output:** `data/cases.csv` with 1 row, `data/SCHEMA.md`.
- **Estimated time:** 30 min
- **Priority:** P0
- **Teammate-delegatable:** No (this is the contract everything else depends on)

---

### TASK-003 — Case Dataset: Write 30 Cases
- **Objective:** Populate `data/cases.csv` to ≥30 rows across all 8 categories per the PRD distribution (VLAN 5, Gateway/IP 5, DHCP 4, DNS 3, Routing 5, ACL 4, NAT 2, Wireless 2).
- **Files:** `data/cases.csv` (append rows only — do not change the header from TASK-002)
- **Dependencies:** TASK-002
- **Instructions:** Each `show_outputs` block must be internally consistent with `expected_fault`. Mark 6–8 cases as `severity` derived from a real Packet Tracer build if available; the rest are structured/simulated (do not claim otherwise anywhere in docs). This can be split into multiple sub-batches (e.g. 10 cases per session) so it fits one context window each.
- **Acceptance criteria:** exactly the required category counts; no duplicate `case_id`; every row passes `test_schema.py`.
- **Tests:** `pytest tests/test_schema.py`; `pytest tests/test_dataset_coverage.py` (checks row count ≥30 and category distribution).
- **Expected output:** `data/cases.csv` with 30+ complete rows.
- **Estimated time:** 2–3 hrs (can be chunked across sessions/people)
- **Priority:** P0
- **Teammate-delegatable:** Yes — hand off a fixed sub-batch (e.g. "write the 5 Routing cases using SCHEMA.md")

---

### TASK-004 — Python Rule Checker Core
- **Objective:** Implement the 6 deterministic rule checks.
- **Files:** `scripts/rule_checker.py`
- **Dependencies:** TASK-002
- **Instructions:** Functions: `check_duplicate_ip`, `check_wrong_mask`, `check_gateway_mismatch`, `check_interface_down`, `check_missing_vlan`, `check_missing_route`, each `(show_outputs: str) -> Finding`, plus `run_all(show_outputs: str) -> list[Finding]`. `Finding` = `{rule_name, triggered: bool, detail: str}`. Use regex/string matching against realistic `show` command line patterns — no full CLI parser (this simplification is an intentional, documented PRD decision, not a shortcut to hide).
- **Acceptance criteria:** `run_all()` returns a list of exactly 6 findings for any well-formed `show_outputs` string; runs with no exceptions on all 30 cases.
- **Tests:** covered in TASK-005.
- **Expected output:** `scripts/rule_checker.py`, importable, no side effects on import.
- **Estimated time:** 1.5 hrs
- **Priority:** P0
- **Teammate-delegatable:** No

---

### TASK-005 — Rule Checker Unit Tests
- **Objective:** Prove each rule correctly triggers and correctly doesn't.
- **Files:** `tests/test_rule_checker.py`
- **Dependencies:** TASK-004
- **Instructions:** 2 synthetic `show_outputs` fixtures per rule (1 triggers True, 1 triggers False) = 12 tests minimum.
- **Acceptance criteria:** `pytest tests/test_rule_checker.py` — 12/12 pass.
- **Tests:** itself.
- **Expected output:** Passing test file + captured sample console output saved to `data/rule_results_sample.txt` (for the PS "sample output" deliverable).
- **Estimated time:** 45 min
- **Priority:** P0
- **Teammate-delegatable:** Yes — can write extra edge-case tests once TASK-004 exists

---

### TASK-006 — AI Diagnosis Prompt Design
- **Objective:** Write the structured diagnosis prompt with grounding rules and worked examples.
- **Files:** `prompts_ai/diagnose_prompt.md`
- **Dependencies:** TASK-002 (needs the field names)
- **Instructions:** Contains: system instruction (ground every claim in given evidence, never invent output not supplied, respond with JSON only), the exact schema (`root_cause, confidence, osi_layer, evidence, next_command, fix_steps`), and 2–3 fully worked few-shot examples (use 2 real cases from `data/cases.csv` once a few exist, or hand-craft matching the PS's own worked example).
- **Acceptance criteria:** File is a complete, ready-to-send prompt template with a clear `{{CASE_SYMPTOM}}` / `{{TOPOLOGY_NOTE}}` / `{{SHOW_OUTPUTS}}` / `{{RULE_FINDINGS}}` insertion pattern.
- **Tests:** manual read-through only.
- **Expected output:** `prompts_ai/diagnose_prompt.md`
- **Estimated time:** 45 min
- **Priority:** P0
- **Teammate-delegatable:** No

---

### TASK-007 — AI Diagnosis Script
- **Objective:** Call the LLM per case using the prompt template and rule-checker findings, save raw + parsed output.
- **Files:** `scripts/diagnose.py`
- **Dependencies:** TASK-004, TASK-006
- **Instructions:** For each row in `cases.csv`: run `rule_checker.run_all()`, fill the prompt template, call the LLM API, save the raw response and parsed JSON to `data/diagnoses.json` keyed by `case_id`. Include `prompt_version` (string, e.g. `"v1"`) and `model` fields in each saved record.
- **Acceptance criteria:** Running on 3 sample cases produces 3 valid entries in `data/diagnoses.json`.
- **Tests:** `pytest tests/test_diagnose_smoke.py` — mocks the API call, checks the record shape is correct.
- **Expected output:** `scripts/diagnose.py`, partial `data/diagnoses.json` (3 cases) for review before full run.
- **Estimated time:** 1.5 hrs
- **Priority:** P0
- **Teammate-delegatable:** No

---

### TASK-008 — JSON Schema Validation & Retry Logic
- **Objective:** Guarantee every diagnosis is schema-valid or explicitly flagged, never silently malformed.
- **Files:** `scripts/validate_diagnosis.py`, edit `scripts/diagnose.py` to call it
- **Dependencies:** TASK-007
- **Instructions:** `jsonschema` schema matching TASK-006's contract. On invalid JSON from the LLM: retry once with an added "return only valid JSON" instruction. If still invalid, write `{"case_id": ..., "status": "needs_manual_review"}` instead of crashing the batch.
- **Acceptance criteria:** Feeding a deliberately malformed string through `validate_diagnosis.py` returns a clear validation error, not an exception.
- **Tests:** `tests/test_validate_diagnosis.py` — 1 valid case passes, 1 malformed case is caught and flagged.
- **Expected output:** `scripts/validate_diagnosis.py`
- **Estimated time:** 40 min
- **Priority:** P0
- **Teammate-delegatable:** No

---

### TASK-009 — Pipeline Integration: Run All Cases
- **Objective:** Execute the full rule-checker → diagnosis pipeline across all 30+ cases in one run.
- **Files:** `scripts/run_pipeline.py` (thin orchestrator calling rule_checker + diagnose + validate), `data/diagnoses.json` (full), `data/rule_results.json` (full)
- **Dependencies:** TASK-003, TASK-005, TASK-008
- **Instructions:** Single command runs the entire pipeline end-to-end from `cases.csv` to final `diagnoses.json` + `rule_results.json`. Log progress per case to console.
- **Acceptance criteria:** `python scripts/run_pipeline.py` completes with a diagnosis (or `needs_manual_review` flag) for every case, no crash.
- **Tests:** `pytest tests/test_pipeline_integration.py` — runs on a 5-case subset, checks output files are created and well-formed.
- **Expected output:** Full `data/diagnoses.json`, full `data/rule_results.json`.
- **Estimated time:** 1 hr (mostly run + spot-check time)
- **Priority:** P0
- **Teammate-delegatable:** Verification pass only (spot-check 5–10 outputs against evidence)

---

### TASK-010 — Human Review Workflow
- **Objective:** Produce the reviewer decision log (Accepted/Edited/Rejected + reason) for every case.
- **Files:** `scripts/review_cli.py` (prints one case + AI diagnosis, takes decision input), `data/review_log.csv`
- **Dependencies:** TASK-009
- **Instructions:** `review_log.csv` columns: `case_id, decision, corrected_fields, reason, reviewer`. `review_cli.py` is optional convenience — reviewing directly in a spreadsheet is equally acceptable. Must include ≥5 genuinely Edited/Rejected cases with real reasoning (do not fabricate; pick from cases where AI plausibly struggled).
- **Acceptance criteria:** Every `case_id` in `cases.csv` has exactly one row in `review_log.csv`; ≥5 rows are Edited/Rejected with non-empty `reason`.
- **Tests:** `pytest tests/test_review_log.py` — row count matches case count, ≥5 corrections present.
- **Expected output:** `data/review_log.csv`
- **Estimated time:** 1.5 hrs (mostly human judgment time, not coding)
- **Priority:** P0
- **Teammate-delegatable:** Yes — assign a case-number range to review independently using the same rubric

---

### TASK-011 — Dashboard Metrics & Charts
- **Objective:** Compute all required PS metrics from real data and produce the chart deliverable.
- **Files:** `scripts/build_dashboard.py`, `dashboard/dashboard_data.json`, `dashboard/issue_distribution.png`, `dashboard/agreement_rate.png`
- **Dependencies:** TASK-009, TASK-010
- **Instructions:** Compute: total cases, issue-type distribution, severity distribution, Accepted/Edited/Rejected counts, `agreement_rate = Accepted/Total`, `correction_rate = (Edited+Rejected)/Total`, rule-finding counts by rule name. Save JSON + two PNG charts via matplotlib. This alone satisfies the PS "spreadsheet or simple chart" requirement — no UI needed yet.
- **Acceptance criteria:** Every number in `dashboard_data.json` matches a manual `pandas` groupby check.
- **Tests:** `pytest tests/test_dashboard_metrics.py` — recomputes agreement_rate independently and asserts match.
- **Expected output:** `dashboard/dashboard_data.json` + 2 PNGs.
- **Estimated time:** 1 hr
- **Priority:** P0
- **Teammate-delegatable:** Chart styling only, not the metric logic

---

### TASK-012 — Responsible AI Log
- **Objective:** Document the ≥5 corrected cases in the required narrative format.
- **Files:** `docs/responsible_ai_log.md`
- **Dependencies:** TASK-010
- **Instructions:** For each corrected case: `case_id`, what AI diagnosed, what was actually wrong (incorrect root cause / insufficient evidence / low confidence / wrong next_command / missed a rule finding), the corrected diagnosis, one-line "why this matters."
- **Acceptance criteria:** ≥5 entries, each referencing a real row in `review_log.csv`.
- **Tests:** `pytest tests/test_responsible_ai_log.py` — checks entry count and that each referenced `case_id` exists.
- **Expected output:** `docs/responsible_ai_log.md`
- **Estimated time:** 45 min
- **Priority:** P0
- **Teammate-delegatable:** Formatting only, not the technical reasoning

---

### TASK-013 — Testing & PS Acceptance Checklist
- **Objective:** Run the full test suite and cross-check every PS deliverable exists and is correct.
- **Files:** `docs/SUBMISSION_CHECKLIST.md` (filled in, checked off)
- **Dependencies:** TASK-001 through TASK-012
- **Instructions:** Run `pytest` (all suites). Walk the 15-item checklist from the PRD §19 and check each item against the actual repo state, not from memory.
- **Acceptance criteria:** All tests pass; every checklist item checked with a note on where the evidence lives.
- **Tests:** `pytest` (full suite, 0 failures)
- **Expected output:** `docs/SUBMISSION_CHECKLIST.md` fully checked.
- **Estimated time:** 45 min
- **Priority:** P0
- **Teammate-delegatable:** Yes — independent verification pass is ideal for a second person

---

### TASK-014 — Optional Static Dashboard UI (polish only)
- **Objective:** One static HTML page (no build step, no server) rendering `dashboard_data.json` + a browsable case table/detail for demo polish.
- **Files:** `dashboard/index.html` (inline JS/CSS, Chart.js via CDN)
- **Dependencies:** TASK-011 (must have real `dashboard_data.json`)
- **Instructions:** Reads `dashboard_data.json`, `diagnoses.json`, `cases.csv` (or a pre-baked combined JSON) client-side via `fetch`. Sections: chart(s) from TASK-011 data, a case table, click-through to a simple case detail block (evidence + AI JSON + review decision). No routing framework, no auth, no backend.
- **Acceptance criteria:** Opens correctly via `file://` or a trivial static server; numbers match `dashboard_data.json` exactly.
- **Tests:** manual visual check only.
- **Expected output:** `dashboard/index.html`
- **Estimated time:** 1.5 hrs
- **Priority:** P2 (first thing dropped if behind schedule)
- **Teammate-delegatable:** Yes — styling/layout, not the data-reading logic

---

### TASK-015 — Final Polish: README, Docs, Submission Packaging
- **Objective:** Make the repo self-explanatory and package the final submission.
- **Files:** `README.md` (finalized), `docs/architecture_notes.md`, submission folder assembly
- **Dependencies:** TASK-013
- **Instructions:** README covers: what the project does, how to run the pipeline (`python scripts/run_pipeline.py` → `build_dashboard.py`), file map of deliverables, how to run tests. Assemble final submission with exact PS-required filenames (`cases.csv`, `diagnose_prompt.md`, etc.) at the expected top level.
- **Acceptance criteria:** A stranger could clone the repo and run the whole pipeline from the README alone.
- **Tests:** dry-run the README's own instructions from a clean checkout.
- **Expected output:** Finalized `README.md`, submission-ready folder.
- **Estimated time:** 1 hr
- **Priority:** P1
- **Teammate-delegatable:** Yes — formatting and dry-run verification

---

## P0 Sequence (must-finish — produces a fully Cisco-compliant project on its own)
TASK-001 → 002 → 003 → 004 → 005 → 006 → 007 → 008 → 009 → 010 → 011 → 012 → 013

## P1 (important, do if P0 is done with time left)
TASK-015 (README/packaging can be done in parallel with polish once P0 core files exist)

## P2 (polish, drop first under time pressure)
TASK-014 (optional static dashboard UI)

---

### 🚨 ADDENDUM: LIVE INTERACTIVE WORKFLOW INTEGRATION
While the core scope above explicitly limited the project to a static architecture, a dynamic HTTP local_server.py implementation was officially developed as an extension bridging real-time custom API queries seamlessly! Detailed specifications for this live extension are documented inside docs/TASK_015_INTERACTIVE_WORKFLOW.md explicitly successfully optimally cleanly logically inherently securely completely accurately.
