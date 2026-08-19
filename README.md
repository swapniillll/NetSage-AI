# NetSage AI

NetSage AI is a Cisco network troubleshooting assistant that helps engineers diagnose networking issues. It combines deterministic Python rules with Gemini-based reasoning to analyze command-line evidence and suggest accurate fixes.

## Project Overview

NetSage AI is designed to accelerate problem resolution in Cisco environments. By running raw `show` command outputs through a strict deterministic rule checker first, and then passing those findings to the Gemini large language model, the system provides accurate, contextual troubleshooting advice while mitigating the risk of AI hallucination.

## Why Two Pipelines?

The project includes two distinct execution pipelines to serve different evaluation and operational needs. 

1. **Historical 30-case pipeline**
   - Evaluates 30 fixed Cisco troubleshooting cases used as a baseline.
   - Takes pre-defined evidence from a CSV file.
   - Runs deterministic rule checking to find physical network states.
   - Generates a Gemini diagnosis based on the rules and symptoms.
   - Validates the output schema, forcing retries if formatting fails.
   - Includes a human review phase to score the AI's accuracy.
   - Populates dashboard and evaluation metrics to prove baseline reliability.

2. **Live Interactive pipeline**
   - Allows an engineer to enter a completely new network problem through the Live Diagnosis interface.
   - Takes custom symptom, topology information, and show-command evidence.
   - The browser sends the request to `local_server.py`.
   - The existing `rule_checker.py` and `diagnose.py` logic are reused for the new input.
   - Gemini produces a custom diagnosis.
   - Validation and retry logic ensures strict JSON output.
   - Human Review allows the engineer to accept, edit, or reject the AI's logic.
   - Packet Tracer verification confirms the fix is manually tested.
   - Saves the interaction to the session history.

The Live Workflow is an extension of the original 30-case project. It does not replace the historical benchmark.

## Architecture / Data Flow

```text
Historical:
30 Cases
  ↓
Evidence
  ↓
Rule Checker
  ↓
Gemini Diagnosis
  ↓
Validation
  ↓
Human Review
  ↓
Dashboard Metrics
```

```text
Live:
User Input
  ↓
dashboard/app.js
  ↓
local_server.py
  ↓
rule_checker.py
  ↓
diagnose.py
  ↓
Gemini
  ↓
Validation / Retry
  ↓
Human Review
  ↓
Packet Tracer Verification
  ↓
Live Session History
```

## Human Review

Because AI can make mistakes, every diagnosis must pass through a strict Human Review checkpoint. An engineer must choose one of three actions:

- **Accept**: The diagnosis is completely correct and safe.
- **Edit**: The diagnosis requires minor corrections by the engineer to be accurate. The original AI diagnosis is preserved as a permanent record, and the human-edited diagnosis is stored separately as `edited_diagnosis`.
- **Reject**: The diagnosis is incorrect or unsafe and is discarded with a provided rationale.

## Cisco Packet Tracer

NetSage does not directly control Cisco Packet Tracer. It analyzes troubleshooting evidence and recommends a fix. The engineer manually applies and verifies the fix in Packet Tracer.

## Security

Protecting credentials and infrastructure is a priority in this architecture:

- `GEMINI_API_KEY` is stored locally in `.env`.
- The browser does not receive the API key under any circumstance.
- The `.env` file must never be committed to version control.
- An `.env.example` file is provided which contains only a placeholder.
- Live session data is stored separately from historical benchmark data to prevent contamination of the baseline testing dataset.

## Technology Stack

- Python
- HTML
- CSS
- Vanilla JavaScript
- Google Gemini / google-genai
- pandas
- jsonschema
- pytest
- python-dotenv
- Cisco Packet Tracer

## Local Setup

To run the project locally, open a PowerShell terminal and execute the following commands:

```powershell
git clone <repository-url>
cd NetSage-AI
python -m pip install -r requirements.txt
```

Create your environment file manually:
1. Copy `.env.example` to `.env`.
2. Open `.env` and configure your API key:
   `GEMINI_API_KEY=YOUR_KEY_HERE`

Launch the local server:
```powershell
python scripts/local_server.py
```

Finally, open your browser and navigate to:
http://127.0.0.1:8080/

## Testing

40 tests passed in 11.95s

Command:
```powershell
python -m pytest tests/ -q
```

## Important Files

- `dashboard/index.html`: The main user interface for the application.
- `dashboard/app.js`: Client-side logic handling HTTP requests and UI state.
- `dashboard/styles.css`: Styling for the dashboard interface.
- `scripts/local_server.py`: The HTTP server managing the Live Interactive API endpoints.
- `scripts/rule_checker.py`: Deterministic logic that analyzes CLI outputs for exact string patterns.
- `scripts/diagnose.py`: Constructs the prompt and queries the Gemini API.
- `scripts/validate_diagnosis.py`: Enforces the JSON schema and handles retry fallbacks.
- `scripts/run_pipeline.py`: Orchestrates the batch execution of the historical 30 cases.
- `data/cases.csv`: The input dataset of 30 locked Cisco scenarios.
- `data/diagnoses.json`: The pipeline's AI output for the historical dataset.
- `data/rule_results.json`: The rule checker's findings for the historical dataset.
- `data/review_log.csv`: The human review decisions for the benchmark evaluation.
- `dashboard/live_sessions.json`: The persistence file for the Live Interactive workflow.

Additional detailed documentation can be found in:
- `CODEBASE_MASTER_STUDY_GUIDE.md`
- `docs/LIVE_WORKFLOW_ARCHITECTURE.md`
- `docs/LOCAL_DEMO_SETUP.md`
- `docs/TASK_015_INTERACTIVE_WORKFLOW.md`
- `docs/FINAL_LIVE_WORKFLOW_VERIFICATION.md`

## Project Scope

This project was built as a local SIP internship project/demo. It is NOT a cloud-hosted production deployment.
