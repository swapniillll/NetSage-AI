import json
import threading
from http.server import HTTPServer
import pytest
import urllib.request
import time
from scripts.local_server import NetSageHTTPRequestHandler

@pytest.fixture(scope="module")
def start_server():
    server = HTTPServer(('localhost', 8081), NetSageHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    time.sleep(1)
    yield "http://localhost:8081"
    server.shutdown()
    server.server_close()

def test_get_cases(start_server):
    req = urllib.request.Request(f"{start_server}/api/cases", method="GET")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        assert len(data) > 0
        assert "case_id" in data[0]

def test_run_rules(start_server):
    payload = json.dumps({"show_outputs": "show ip interface brief\nGigabitEthernet0/0 unassigned NO unset administratively down down"}).encode('utf-8')
    req = urllib.request.Request(
        f"{start_server}/api/rules", 
        data=payload,
        headers={'Content-Type': 'application/json'},
        method="POST"
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        assert len(data) == 6
        assert isinstance(data, list)
        
def test_diagnose_no_api_key(start_server, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    # Tests that without api key, it safely fails via local bridge 
    payload = json.dumps({"session_id": "test", "symptom": "a", "topology": "b", "show_outputs": "c"}).encode('utf-8')
    req = urllib.request.Request(
        f"{start_server}/api/diagnose", 
        data=payload,
        headers={'Content-Type': 'application/json'},
        method="POST"
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        assert e.code == 400
        data = json.loads(e.read().decode())
        assert "GEMINI_API_KEY env variable not set" in data['message']

