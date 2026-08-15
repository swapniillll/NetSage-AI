# 006 — AI Diagnosis Prompt Design

## Context
`data/SCHEMA.md` defines the case fields. `data/cases.csv` has some real cases available by now (TASK-003 may still be in progress — that's fine, a few rows are enough to build worked examples from). Read `data/SCHEMA.md` and a couple of rows from `data/cases.csv` before writing this.

## Task
Write the structured diagnosis prompt template that will be sent to the LLM for every case.

## Files
Create: `prompts_ai/diagnose_prompt.md`. Do not create any other prompt-related files.

## Requirements
- System instruction: the assistant is a senior network engineer helper; must ground every claim only in the evidence given (symptom, topology note, show outputs, rule-checker findings); must never invent command output it wasn't given; if evidence is insufficient it must say so and lower confidence; must respond with valid JSON only, nothing else.
- Exact output schema (matches PS fields, no extra fields): `root_cause` (string), `confidence` (float 0–1), `osi_layer` (string), `evidence` (array of strings, each referencing actual supplied show-output lines), `next_command` (string), `fix_steps` (array of strings).
- Include 2–3 fully worked few-shot examples, using real or PS-provided example cases (the PS's own worked example — VLAN30/ACL case — is a good one to include).
- Clear placeholder markers for insertion: `{{SYMPTOM}}`, `{{TOPOLOGY_NOTE}}`, `{{SHOW_OUTPUTS}}`, `{{RULE_FINDINGS}}`.

## Acceptance criteria
The file is a complete, directly-usable prompt — reading it top to bottom, a human could manually run one case through an LLM by hand and get a correctly-shaped JSON response.

## Tests
None (prompt-authoring task). Manual read-through for clarity and schema correctness.

## Documentation
Update `PROJECT_STATE.md`: check off TASK-006, log `prompts_ai/diagnose_prompt.md`.

## Git
Commit: `TASK-006: diagnosis prompt template + worked examples`
