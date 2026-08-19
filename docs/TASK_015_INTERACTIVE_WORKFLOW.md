# TASK 015: NetSage AI Interactive Workflow Upgrade

## Overview
The NetSage AI project previously featured a static presentation dashboard meant for historical analysis. To provide a professional, demonstrable troubleshooting workflow without risking API key leakage to the frontend or modifying verified core logic, an interactive bridge has been implemented.

This upgrade implements a full **8-Stage Troubleshooting Lifecycle**:
1. Case Loading (Evidence Gathering)
2. Deterministic Rule Checking
3. LLM API Invocation
4. JSON Schema Validation / Retry / Fallback
5. Human Review (Accept / Edit / Reject)
6. Engineer Fix Action Recommendation
7. Cisco Packet Tracer Verification
8. Case Status Finalization

## Architecture Modifications
### Security & The Local Bridge Adapter
The browser UI is prohibited from securely managing the `GEMINI_API_KEY`. Rather than mutating the static dashboard generation into a Node API, we kept the tech stack isolated:

- **`scripts/local_server.py`**: A new, zero-dependency Python bridge utilizing `http.server`. 
- When run, it mounts the `dashboard/` static files at `http://localhost:8080/`.
- It exports four secure endpoints:
  - `GET /api/cases`: Loads `cases.csv` using the `csv` module.
  - `POST /api/rules`: Directly calls `scripts.rule_checker.run_all` and returns outcomes.
  - `POST /api/diagnose`: Imports `scripts.diagnose` components. It handles securely loading the `.env` API key from the local environment, fetching the prompt from python functions, executing the remote `google-genai` calls, and natively handing fallback logic using validation functions.
  - `POST /api/review` and `POST /api/verify`: Records decisions and actions into transient presentation logs (`session_reviews.json` and `session_verifications.json`) keeping the core static logs unpolluted.

### Frontend Overhaul (`dashboard/index.html` & `app.js`)
The `Diagnose` view has been completely rewritten.
- Replaced the vulnerable "Paste API Key" implementation with structured dropdowns routing traffic to the local adapter.
- Separated "Run Rule Check" and "Run AI Diagnosis" execution barriers to cleanly demonstrate deterministic vs non-deterministic workflows.
- Implemented state-based rendering to show the progression of the case investigation sequentially.

## How to Run the Interactive Workflow
1. Ensure your Google API Key is securely placed in the root directory inside an `.env` file (`GEMINI_API_KEY=YOUR_KEY`).
2. Run the new local bridge via Python:
   ```bash
   python scripts/local_server.py
   ```
3. Open `http://localhost:8080/` in an internet browser.
4. Navigate to the **"Diagnose"** tab on the navigation sidepane.
5. In the Load Case section, select an existing issue to populate evidence.
6. Click **"Run Rule Check"** to execute regex verification.
7. Click **"Run AI Diagnosis"** to invoke Gemini with the populated prompt.
8. Evaluate the findings in the active result board, supply a decision to the **Human Review** panel, and optionally verify fix output manually.

## Verification
- Core tests remain unaltered to guarantee the integrity of data outputs.
- A new test file `tests/test_local_server.py` verifies `/api/rules`, `/api/diagnose`, and configuration failures using Python's unified `urllib.request`.
