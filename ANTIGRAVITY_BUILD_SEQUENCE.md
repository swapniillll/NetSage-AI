# NetSage AI — Antigravity/Cursor Build Sequence

Each task follows the same loop. Do not skip steps, even when a task feels trivial — the Documentation-update step is what makes the project context-safe across dropped sessions.

```text
Task
↓
Implementation
↓
Test
↓
Documentation update  (PROJECT_STATE.md: mark done, list files touched, note anything half-finished)
↓
Git commit             (message = "TASK-0XX: <short description>")
↓
Next task
```

## Full ordered sequence (P0 core first, then P1, then P2)

1. TASK-001 — Project Setup & Repo Scaffold
2. TASK-002 — Data Schema & `cases.csv` Template
3. TASK-003 — Case Dataset: Write 30 Cases
4. TASK-004 — Python Rule Checker Core
5. TASK-005 — Rule Checker Unit Tests
6. TASK-006 — AI Diagnosis Prompt Design
7. TASK-007 — AI Diagnosis Script
8. TASK-008 — JSON Schema Validation & Retry Logic
9. TASK-009 — Pipeline Integration: Run All Cases
10. TASK-010 — Human Review Workflow
11. TASK-011 — Dashboard Metrics & Charts
12. TASK-012 — Responsible AI Log
13. TASK-013 — Testing & PS Acceptance Checklist
   **← P0 sequence complete here. Project is fully Cisco-PS-compliant at this point.**
14. TASK-015 — Final Polish: README, Docs, Submission Packaging (P1)
15. TASK-014 — Optional Static Dashboard UI (P2 — only if time remains)

## Rules for the coding agent

- **Never start a task without reading `PROJECT_STATE.md` first.** It tells you exactly what exists and what doesn't — do not assume anything from a prior conversation.
- **Never touch files outside a task's declared "Files" list.** If a task seems to require touching something else, stop and flag it rather than silently expanding scope.
- **Every task ends with a passing test run relevant to that task**, before the commit. A task is not "done" if its own tests aren't passing.
- **Commit after every task, not after every session.** Small commits mean a dropped session loses at most one task's worth of work.
- **If a task is interrupted mid-way:** leave a `<!-- INCOMPLETE: reason -->` comment at the top of the file being edited, and note it explicitly in `PROJECT_STATE.md` under "In Progress" before stopping. The next session must check for this before continuing.
- **Dependencies are hard blockers.** Do not start TASK-007 before TASK-004 and TASK-006 are both marked done in `PROJECT_STATE.md`, even if the code might "probably still work."
- **P2 tasks are always safe to abandon.** If TASK-014 doesn't get started, the project is still complete and submittable per §13's acceptance criteria.
