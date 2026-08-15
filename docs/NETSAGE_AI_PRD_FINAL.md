# NetSage AI — Final Product Requirements Document (PRD)

**Status:** Approved — locked for build. Source documents: Cisco NetAcad PS (`AI_Problem_Statement__1_.docx`), `NETSAGE_AI_MASTER_BUILD_PLAN.md`, `TASK_BOARD.md`, `ANTIGRAVITY_BUILD_SEQUENCE.md`, `prompts/001–015`.
This PRD does not redesign anything — it consolidates every decision already made across those files into one authoritative reference the build (and the viva) is measured against.

---

## 1. Product Summary

**NetSage AI** is an AI-assisted troubleshooting helper for Cisco/Packet Tracer lab networks. Given a symptom, topology note, and `show`-command output, it produces a structured, evidence-grounded diagnosis (root cause, OSI layer, confidence, next command, fix steps) that a human reviewer must accept, edit, or reject before it counts as final. It is built as a **file-based Python pipeline**, not a web application — every required deliverable is a file the pipeline produces.

**In one sentence (PS's own framing):** an AI-assisted troubleshooter for Packet Tracer lab problems that reads symptoms and show-command output, suggests likely causes and next steps, and always requires a human to review before accepting the fix.

---

## 2. Problem Statement (source: Cisco PS)

Junior network engineers know individual commands but struggle to connect a symptom to its real root cause — a PC that gets an IP but can't reach a server could be a VLAN, routing, DHCP, DNS, ACL, or NAT problem. NetSage AI helps close that gap while keeping a human accountable for every final diagnosis, per the PS's own **Safety Rule: human review**.

---

## 3. Goals

- Satisfy every explicit Cisco PS requirement (§5) with real, working evidence — not simulated or claimed-but-unverified.
- Demonstrate the full loop end-to-end: **symptom → evidence → deterministic rule check → AI diagnosis → human review → fix → verification.**
- Keep the system explainable: every number on the dashboard and every AI claim must be traceable to a real file the person can point to in the viva.
- Ship inside the real constraint: ~2 days, effectively solo, heavy AI-coding-agent assistance.

## 4. Non-Goals (explicitly out of scope — do not build)

- Any authentication, login, registration, or user roles.
- Any relational database (PostgreSQL) or ORM (Prisma).
- Any backend service/API layer (FastAPI or otherwise) — the rule checker is a Python function call, not a network call.
- Any deployment/hosting infrastructure — the deliverable is a repo + files + a video, run locally.
- A full Cisco CLI configuration parser — the rule checker uses a documented, simplified regex-based evidence representation instead (§9).
- Generic AI chatbot, generic dashboard product, or generic case-management CRUD app — the product stays anchored to Cisco troubleshooting end to end.

---

## 5. Requirements (traced to Cisco PS, verbatim scope)

| # | Requirement | Source | Priority |
|---|---|---|---|
| R1 | ≥30 troubleshooting cases, covering VLAN, gateway/IP, DHCP, DNS, routing, ACL, NAT, wireless | PS "What You Must Build" | P0 |
| R2 | Each case has: symptom, topology note, show outputs, expected fault, OSI layer, concept tag, severity | PS | P0 |
| R3 | Structured AI prompt library returning JSON: root_cause, confidence, evidence, next_command, fix_steps; includes 2–3 worked examples | PS | P0 |
| R4 | Python rule checker with deterministic checks: duplicate IP, wrong mask, gateway mismatch, interface down, missing VLAN, missing route | PS | P0 |
| R5 | AI diagnosis run against every case, compared to the known expected answer | PS | P0 |
| R6 | Human review: every case marked Accepted / Edited / Rejected, with reasoning logged | PS | P0 |
| R7 | Responsible AI log: ≥5 cases where the AI's answer was genuinely corrected by a human | PS | P0 |
| R8 | Dashboard: simple summary of issue types, severity, and AI-vs-human agreement (spreadsheet or simple chart is explicitly sufficient) | PS | P0 |
| R9 | Demo: one broken lab diagnosed, reviewed, fixed, and verified, 5–10 min video | PS | P0 |
| R10 | AI responses must quote/reference actual show-command evidence (graded check) | PS | P0 |
| R11 | Deliverable files present with correct names: `cases.csv`, `diagnose_prompt.md` (+ helpers), Python checker + sample output, dashboard artifact, responsible AI log, demo video | PS | P0 |

Everything else in this PRD exists only to satisfy R1–R11 with acceptable engineering quality — no requirement is added beyond this table.

---

## 6. System Architecture (final, locked)

```
data/cases.csv  (source of truth — R1, R2, R11)
        │
        ▼
scripts/rule_checker.py  ──►  data/rule_results.json / sample.txt   (R4)
        │
        ▼
scripts/diagnose.py + scripts/validate_diagnosis.py
   (loads case + rule findings → prompts_ai/diagnose_prompt.md → LLM →
    schema-validated JSON, retry-once, else flagged needs_manual_review)
        ▼
data/diagnoses.json   (R3, R5, R10)
        │
        ▼
data/review_log.csv   (manual Accept/Edit/Reject pass — R6, feeds R7)
        │
        ▼
scripts/build_dashboard.py ──► dashboard/dashboard_data.json + charts   (R8)
        │
        ▼
docs/responsible_ai_log.md (R7)  +  demo video (R9)
```

No layer above requires a server process, a database, or authentication. `scripts/run_pipeline.py` is the single orchestrating entrypoint that ties rule-checking and diagnosis together end to end.

**Optional, P2 only:** `dashboard/index.html` — a static, no-backend HTML+Chart.js page reading the same JSON files, purely for demo polish. It is not required for R8 and is the first thing dropped under time pressure.

---

## 7. Technology Stack (final)

| Layer | Choice | Excluded (and why) |
|---|---|---|
| Data storage | CSV + JSON files | Postgres/Prisma — deliverables are files, a DB adds only risk |
| Rule checker | Plain Python (stdlib + `re`) | FastAPI/service layer — no consumer beyond one script |
| AI calls | Python LLM SDK, single call per case | Multi-agent orchestration — one structured call per case is all R3 needs |
| Validation | `jsonschema` + one retry + fallback flag | — |
| Review | CSV (spreadsheet or tiny CLI) | Any web review UI — not required |
| Metrics | `pandas` + `matplotlib` | Auth-gated analytics dashboard — not required |
| Optional polish | Static HTML + Chart.js (CDN, no build step) | Next.js server routes, routing frameworks, login |
| Tests | `pytest` | — |

---

## 8. Data Model

All entities are files, not database tables:

| Entity | File | Key fields | Required by |
|---|---|---|---|
| Case | `data/cases.csv` | case_id, title, category, symptom, topology_note, show_outputs, expected_fault, osi_layer, concept, severity, expected_next_command, expected_fix | R1, R2, R11 |
| Rule findings | `data/rule_results.json` | case_id, rule_name, triggered, detail | R4 |
| AI Diagnosis | `data/diagnoses.json` | case_id, root_cause, confidence, osi_layer, evidence[], next_command, fix_steps[], prompt_version, model | R3, R5, R10 |
| Human Review | `data/review_log.csv` | case_id, decision, corrected_fields, reason, reviewer | R6 |
| Responsible AI | `docs/responsible_ai_log.md` | narrative per corrected case | R7 |
| Dashboard metrics | `dashboard/dashboard_data.json` + PNGs | category/severity counts, agreement_rate, correction_rate, rule-finding counts | R8 |

`category` enum: `VLAN, Gateway/IP, DHCP, DNS, Routing, ACL, NAT, Wireless`. `decision` enum: `Accepted, Edited, Rejected`.

---

## 9. AI System Design

**Contract (exact, no extra fields):**
```json
{
  "root_cause": "",
  "confidence": 0.0,
  "osi_layer": "",
  "evidence": [],
  "next_command": "",
  "fix_steps": []
}
```
- **System prompt:** ground every claim in supplied evidence only; never invent output not given; state uncertainty via `confidence`; JSON only.
- **Few-shot:** 2–3 worked examples embedded directly in `prompts_ai/diagnose_prompt.md` (matches PS wording exactly).
- **Grounding/anti-hallucination:** model instructed to cite actual `show_outputs` lines in `evidence`; cross-checked against `next_command` appearing in supplied evidence where applicable.
- **Validation:** `jsonschema` check → retry once on failure → flag `needs_manual_review` if still invalid (pipeline never crashes on a bad response).
- **Versioning:** `prompt_version` string recorded per diagnosis record — no separate DB table needed.

## 10. Rule Checker Design

Six functions (`check_duplicate_ip`, `check_wrong_mask`, `check_gateway_mismatch`, `check_interface_down`, `check_missing_vlan`, `check_missing_route`) plus `run_all()`, implemented with regex/string matching against realistic `show`-output text blocks — **not** a full Cisco CLI parser. This is a deliberate, documented simplification: a real parser is high-effort/high-risk for zero additional PS credit, since the requirement is "Python script with deterministic checks," not a general config parser. Every rule has 2 unit tests (trigger / no-trigger).

## 11. Dataset Strategy

30 cases distributed: VLAN 5, Gateway/IP 5, DHCP 4, DNS 3, Routing 5, ACL 4, NAT 2, Wireless 2. 6–8 cases should come from real Packet Tracer builds where feasible (for demo authenticity); the rest are clearly-labeled structured scenarios — never misrepresented as real captures.

## 12. Human Review & Responsible AI

Every case gets exactly one review decision with a reason. ≥5 must be genuine Edited/Rejected cases (deliberately include a few evidence-sparse or ambiguous cases in the dataset so real AI struggles surface honestly rather than being fabricated). Each is written up in `docs/responsible_ai_log.md` with what went wrong, the correction, and why it matters.

## 13. Dashboard & Metrics

Computed, not hardcoded: total cases, issue-type distribution, severity distribution, Accepted/Edited/Rejected counts, `agreement_rate = Accepted/Total`, `correction_rate = (Edited+Rejected)/Total`, rule-finding counts. Output as `dashboard_data.json` + two PNG charts — this alone satisfies R8. Static HTML view is optional polish only.

## 14. Testing Strategy

Unit tests per rule (12+), JSON-schema validation tests, a pipeline integration test on a 5-case subset, a full-suite `pytest` run before submission, and a manually-verified PS acceptance checklist (`docs/SUBMISSION_CHECKLIST.md`) mapping every checklist item to real evidence in the repo.

---

## 15. Execution Plan (reference, not redefined here)

The full task-by-task build plan already exists and is not restated in this PRD — this PRD is the requirements/architecture source of truth those tasks implement against:

- **`TASK_BOARD.md`** — TASK-001 through TASK-015, each with objective/files/dependencies/acceptance criteria/tests/priority/delegation.
- **`ANTIGRAVITY_BUILD_SEQUENCE.md`** — the exact order and the Task→Implementation→Test→Docs→Commit→Next loop.
- **`PROJECT_STATE.md`** — the live tracker every task reads first and updates last, for context-safe resumption.
- **`prompts/001–015`** — individual ready-to-run implementation prompts for the coding agent.

**P0 sequence (must-finish, produces a fully PS-compliant project alone):** TASK-001 → 002 → 003 → 004 → 005 → 006 → 007 → 008 → 009 → 010 → 011 → 012 → 013.
**P1:** TASK-015 (README/docs/packaging).
**P2 (drop first):** TASK-014 (optional static dashboard UI).

---

## 16. Success Metrics / Definition of Done

- Every row in §5's requirements table (R1–R11) has a real, produced artifact — not a claim.
- Full pipeline (`run_pipeline.py` → `build_dashboard.py`) runs end-to-end from a clean checkout without manual patching.
- `pytest` passes with 0 failures across the whole repo.
- Every dashboard number traces to a `pandas` recomputation that matches.
- ≥5 genuine, non-fabricated Responsible AI corrections documented.
- Demo video shows the full loop on one real broken case.
- The builder can defend every section of this PRD in a viva without notes.

## 17. Key Risks (see `NETSAGE_AI_MASTER_BUILD_PLAN.md` §27 for the full register)

LLM API instability, malformed JSON responses, dataset-writing taking longer than planned, AI-agent-generated code needing verification before trust, and general schedule slippage — each has a documented fallback that never compromises R1–R11.

---

*This PRD is final for build purposes. Any change to architecture, scope, or requirements must be reflected here first, then propagated to `TASK_BOARD.md` and the affected `prompts/*.md` files — the task files should never drift from this document.*
