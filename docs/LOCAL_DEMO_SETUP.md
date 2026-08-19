# NetSage-AI Local Demo Setup 🚀

Follow these instructions to safely set up and run the interactive Troubleshooting Workflow on your local machine using the Google Gemini model.

## Prerequisites
- A local checkout of this repository.
- Python 3.9+ installed and configured on your `PATH`.
- A Google API Key with access to the `gemini-3.5-flash-lite` model.
- (Optional) Cisco Packet Tracer installed to perform lab verifications.

## Step 1: Environment & Secrets Setup
The workflow requires a securely configured `.env` file to communicate with Google Gemini without exposing your API keys via Git. 

1. Create a `.env` file in the root of the cloned repository folder (next to `requirements.txt`).
2. Add your Gemini API key to the `.env` file exactly like this:
   ```env
   GEMINI_API_KEY=YOUR_REAL_API_KEY_HERE
   ```
3. Save the `.env` file. Check that `git status` **does not** track the `.env` file.

> **Note:** `.env` is intentionally excluded from Git via `.gitignore` to prevent secret leaks. Never commit your API key.

## Step 2: Install Dependencies
Run the following command in the root folder to install all required dependencies defined in `requirements.txt`:
```bash
python -m pip install -r requirements.txt
```
*(Dependencies include `google-genai`, `python-dotenv`, `pandas`, `pytest`, `matplotlib`, and `jsonschema`.)*

## Step 3: Start the Backend Bridge Server
NetSage uses a local Python web server (`scripts/local_server.py`) to broker API requests between the frontend application and the backend Gemini API. This keeps all secrets safe server-side.

Run the following command from the repository root:
```bash
python scripts/local_server.py
```
*You should see an output similar to `Serving HTTP on 127.0.0.1 port 8080 (http://127.0.0.1:8080/) ...`*

## Step 4: Open the Interactive Dashboard
1. Open a web browser.
2. Navigate to: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)

You will be greeted by the NetSage-AI Dashboard.

## Step 5: Start a Live Troubleshooting Session
To evaluate the end-to-end interactive diagnostic lifecycle, perform the following:

1. Click **"New Live Session"** on the dashboard to generate a secure UUID session identifier (e.g. `LIVE-YYYYMMDD-HHMMSS-XXXX`).
2. Type in a **Symptom** (e.g., "PC 1 can't ping the external server").
3. Type in the **Topology Note** (e.g., "PC 1 is connected to SW1 on VLAN 10").
4. Paste the **Cisco CLI Evidence** you would get dynamically from your Packet Tracer environment (e.g., `show vlan brief`, `show ip interface brief` outputs).
5. Click **"🔍 Run Rule Check"** to perform deterministic regex evaluations to identify blatant faults (like missing VLANs or misconfigured gateways).
6. Click **"⚡ Run AI Diagnosis"** to dynamically synthesize the inputs and rule evaluations into a prompt, pass it to Gemini, and yield a secure and structured JSON-based Root Cause & Fix recommendation list.
7. Perform **Review Options**: 
   - Accept the diagnosis, 
   - explicitly Edit the AI's response while attaching a written reason (persisted asynchronously!), 
   - or entirely Reject the response with reason.
8. Click **"Apply Review Action"** and save the assessment.
9. **Manually apply the recommended fix in your external Packet Tracer environment**. NetSage does not natively edit or automatically configure Packet Tracer devices. You must be the actual executor of the CLI commands!
10. Finally, record the Verification outcome and terminal status. You can reload this audit trail at any time from the **Troubleshooting History** view on the main NetSage-AI Dashboard!
