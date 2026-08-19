import os
import sys
import json
import csv
import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
from dataclasses import asdict

# Resolve paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, ROOT_DIR)

from scripts.rule_checker import run_all
from scripts.diagnose import build_prompt, call_llm, MODEL_NAME, PROMPT_VERSION, load_environment, format_findings
from scripts.validate_diagnosis import validate

CASES_FILE = os.path.join(ROOT_DIR, "data", "cases.csv")
LIVE_SESSIONS_FILE = os.path.join(ROOT_DIR, "dashboard", "live_sessions.json")

def _read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class NetSageHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(ROOT_DIR, "dashboard"), **kwargs)

    def do_GET(self):
        if self.path == '/api/cases':
            self._handle_get_cases()
        elif self.path == '/api/sessions':
            self._handle_get_sessions()
        else:
            # Fallback to static files
            super().do_GET()
            
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        
        # Security Hardening: Max 1MB payload to prevent memory overflow
        if content_length > 1000000:
            self.send_error(413, "Payload Too Large")
            return
            
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON payload."})
            return

        if parsed_path.path == '/api/rules':
            self._handle_rules(payload)
        elif parsed_path.path == '/api/diagnose':
            self._handle_diagnose(payload)
        elif parsed_path.path == '/api/review':
            self._handle_review(payload)
        elif parsed_path.path == '/api/verify':
            self._handle_verify(payload)
        else:
            self.send_error(404, "Not Found")

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _handle_get_cases(self):
        try:
            cases = []
            if os.path.exists(CASES_FILE):
                with open(CASES_FILE, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    cases = [dict(row) for row in reader]
            self._send_json(200, cases)
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _handle_get_sessions(self):
        try:
            sessions = _read_json(LIVE_SESSIONS_FILE)
            self._send_json(200, sessions)
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _handle_rules(self, payload):
        show_outputs = payload.get('show_outputs', '')
        try:
            findings = run_all(show_outputs)
            results = [asdict(f) for f in findings]
            self._send_json(200, results)
        except Exception as e:
            self._send_json(500, {"error": str(e)})
            
    def _handle_diagnose(self, payload):
        show_outputs = payload.get('show_outputs', '')
        symptom = payload.get('symptom', '')
        topology_note = payload.get('topology', '')
        session_id = payload.get('session_id')
        
        if not session_id:
            self._send_json(400, {"error": "Missing session_id."})
            return
            
        if not show_outputs.strip():
            self._send_json(400, {"error": "Missing show_outputs evidence."})
            return
            
        load_environment()
        
        if not os.environ.get("GEMINI_API_KEY"):
            self._send_json(400, {"status": "error", "message": "GEMINI_API_KEY env variable not set. Please set it in .env before running."})
            return

        try:
            findings = run_all(show_outputs)
            rule_findings_str = format_findings(findings)
            prompt_text = build_prompt(symptom, topology_note, show_outputs, rule_findings_str)
            raw_response = call_llm(prompt_text, MODEL_NAME)
            parsed_data = validate(raw_response)
            
            if parsed_data.get("status") == "validation_error":
                retry_prompt = prompt_text + "\\n\\nCRITICAL: your last response was invalid JSON — return only valid JSON matching the schema."
                raw_response_2 = call_llm(retry_prompt, MODEL_NAME)
                parsed_data = validate(raw_response_2)
                
                if parsed_data.get("status") == "validation_error":
                    record = {
                        "session_id": session_id,
                        "status": "needs_manual_review",
                        "raw_response": raw_response_2
                    }
                else:
                    record = {
                        "session_id": session_id,
                        "raw_response": raw_response_2,
                        "parsed_diagnosis": parsed_data,
                        "prompt_version": PROMPT_VERSION,
                        "model": MODEL_NAME
                    }
            else:
                record = {
                    "session_id": session_id,
                    "raw_response": raw_response,
                    "parsed_diagnosis": parsed_data,
                    "prompt_version": PROMPT_VERSION,
                    "model": MODEL_NAME
                }

            # Persist to live_sessions.json
            sessions = _read_json(LIVE_SESSIONS_FILE)
            if session_id not in sessions:
                sessions[session_id] = {
                    "session_id": session_id,
                    "timestamp_created": datetime.datetime.utcnow().isoformat() + "Z",
                    "inputs": {
                        "symptom": symptom,
                        "topology_note": topology_note,
                        "show_outputs": show_outputs
                    }
                }
            sessions[session_id]["ai_diagnosis"] = record
            _write_json(LIVE_SESSIONS_FILE, sessions)

            self._send_json(200, record)
        except Exception as e:
            self._send_json(500, {"status": "error", "message": str(e)})

    def _handle_review(self, payload):
        session_id = payload.get('session_id')
        decision = payload.get('decision')
        if not session_id or not decision:
            self._send_json(400, {"error": "Missing session_id or decision"})
            return
            
        sessions = _read_json(LIVE_SESSIONS_FILE)
        if session_id not in sessions:
            sessions[session_id] = {"session_id": session_id}
            
        payload["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
        sessions[session_id]["review"] = payload
        _write_json(LIVE_SESSIONS_FILE, sessions)
        
        self._send_json(200, {"status": "saved"})

    def _handle_verify(self, payload):
        session_id = payload.get('session_id')
        status = payload.get('status')
        if not session_id or not status:
            self._send_json(400, {"error": "Missing session_id or status"})
            return
            
        sessions = _read_json(LIVE_SESSIONS_FILE)
        if session_id not in sessions:
            sessions[session_id] = {"session_id": session_id}
            
        payload["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
        sessions[session_id]["verification"] = payload
        _write_json(LIVE_SESSIONS_FILE, sessions)
        
        self._send_json(200, {"status": "saved"})

def run(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, NetSageHTTPRequestHandler)
    print(f"Starting local NetSage bridge at http://localhost:{port}/")
    print(f"Serving UI from {os.path.join(ROOT_DIR, 'dashboard')}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run()
