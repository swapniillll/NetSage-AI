# NetSage AI: Live Workflow Architecture

## 1. Goal and Session Boundaries
The live interactive troubleshooting workflow provides Cisco Networking Academy engineers with an ad-hoc local AI assistant for Packet Tracer labs. It is explicitly designed to maintain isolation from the `data/cases.csv` and `data/review_log.csv` historical evaluation datasets to avoid metric contamination.

Every operation performed via the live dashboard initiates a uniquely identifiable session (e.g., `LIVE-YYYYMMDD-HHMMSS-XXXX`). This enables a coherent audit trail through our 8-stage lifecycle.

## 2. Frontend Adapter (`dashboard/app.js`)
The `app.js` UI functions as a strict presentation layer containing state machinary. It handles:
- Capturing user evidence (Symptoms, Topology, `show_outputs`).
- Preventing navigation bypassing (e.g., cannot review before diagnosing).
- Displaying deterministic Rule Findings and structured AI outputs natively.

## 3. The Local Bridge (`scripts/local_server.py`)
To prevent exposing the `GEMINI_API_KEY` to the browser, the frontend interfaces securely with `local_server.py`. 
Key security implementations:
- Hard payload size limit (Max 1MB).
- Server-side environment binding (`load_environment()`).

## 4. Pipeline Execution
1. **Rule Checker Integration**: UI requests `/api/rules`. The server proxies `show_outputs` directly into the original deterministic `scripts.rule_checker.run_all` functions.
2. **AI Integration (`/api/diagnose`)**: UI issues a diagnosis POST request. 
   - `build_prompt` stitches evidence, finding strings, and symptom details together.
   - `call_llm` interfaces with `gemini-3.5-flash-lite`.
3. **Validation & Retry**: `validate_diagnosis.validate` tests the response natively. If the JSON is invalid, the bridge triggers an automated prompt retry. Multiple failures yield a strict `needs_manual_review` state, preventing broken JSON UI ingestion.

## 5. Human Review & Responsible AI
In the UI, diagnoses require explicit Human review.
- Accept: Approves the output.
- Edit: The reviewer explicitly corrects fields. The backend preserves the `original_ai_diagnosis` payload natively inside the JSON session store.
- Reject: Rejection strictly enforces a textual `Reason`.

## 6. Verification
NetSage-AI does not manipulate Cisco Packet Tracer automatically. The engineer copies the Recommended Fix, types it into the simulator, and explicitly pushes back terminal evidence verifying success/failure alongside a `VERIFIED` state change via `/api/verify`.

## 7. Persistence and Session History (`dashboard/live_sessions.json`)
The `local_server.py` implements a scalable `dict`-based JSON write mechanism isolated directly to `dashboard/live_sessions.json`. Using `/api/sessions`, the `app.js` renders a "Troubleshooting History" audit table ensuring full lifecycle traceability while protecting the `build_dashboard.py` historical baselines.
