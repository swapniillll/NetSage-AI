import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Ensure we can import from scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, ROOT_DIR)

from scripts.local_server import NetSageHTTPRequestHandler

class MockServer:
    def __init__(self):
        pass

class MockRequest:
    def makefile(self, *args, **kwargs):
        from io import BytesIO
        return BytesIO(b"")

def make_request(path, payload, mock_environ, mock_read, mock_write, mock_llm, mock_rules=None):
    from io import BytesIO
    handler = NetSageHTTPRequestHandler(MockRequest(), client_address=('127.0.0.1', 8080), server=MockServer())
    
    # Mock reading JSON body
    body = json.dumps(payload).encode('utf-8')
    handler.rfile = BytesIO(body)
    handler.headers = {'Content-Length': str(len(body))}
    handler.path = path
    
    # Capture response
    handler.wfile = BytesIO()
    handler._send_json = MagicMock()
    
    handler.do_POST()
    return handler._send_json

def test_missing_session_id():
    handler = NetSageHTTPRequestHandler(MockRequest(), client_address=('127.0.0.1', 8080), server=MockServer())
    handler.rfile = __import__('io').BytesIO(b"{}")
    handler.headers = {'Content-Length': "2"}
    handler.path = "/api/diagnose"
    handler._send_json = MagicMock()
    handler.do_POST()
    
    handler._send_json.assert_called_with(400, {"error": "Missing session_id."})

def test_missing_evidence():
    handler = NetSageHTTPRequestHandler(MockRequest(), client_address=('127.0.0.1', 8080), server=MockServer())
    handler.rfile = __import__('io').BytesIO(b'{"session_id": "TEST"}')
    handler.headers = {'Content-Length': str(len(b'{"session_id": "TEST"}'))}
    handler.path = "/api/diagnose"
    handler._send_json = MagicMock()
    handler.do_POST()
    
    handler._send_json.assert_called_with(400, {"error": "Missing show_outputs evidence."})

@patch("scripts.local_server.call_llm")
@patch("scripts.local_server._write_json")
@patch("scripts.local_server._read_json", return_value={})
@patch("os.environ.get", return_value="fake_api_key")
def test_valid_diagnosis(mock_env, mock_read, mock_write, mock_llm):
    # Mock valid JSON from LLM
    mock_llm.return_value = '```json\n{"root_cause":"Test","confidence":1,"osi_layer":"3","evidence":["e"],"next_command":"show","fix_steps":["fix"]}\n```'
    
    handler = NetSageHTTPRequestHandler(MockRequest(), client_address=('127.0.0.1', 8080), server=MockServer())
    body = json.dumps({
        "session_id": "LIVE-001",
        "show_outputs": "show ip route",
        "symptom": "broken",
        "topology": "switch"
    }).encode('utf-8')
    handler.rfile = __import__('io').BytesIO(body)
    handler.headers = {'Content-Length': str(len(body))}
    handler.path = "/api/diagnose"
    handler._send_json = MagicMock()
    
    handler.do_POST()
    
    args = handler._send_json.call_args[0]
    assert args[0] == 200
    assert args[1]["session_id"] == "LIVE-001"
    assert args[1]["parsed_diagnosis"]["root_cause"] == "Test"
    
    # Check that disk persistence was invoked
    assert mock_write.called

@patch("scripts.local_server._write_json")
@patch("scripts.local_server._read_json", return_value={"LIVE-001": {"session_id":"LIVE-001"}})
def test_review_persistence(mock_read, mock_write):
    handler = NetSageHTTPRequestHandler(MockRequest(), client_address=('127.0.0.1', 8080), server=MockServer())
    body = json.dumps({
        "session_id": "LIVE-001",
        "decision": "Edited",
        "reason": "Test reason"
    }).encode('utf-8')
    handler.rfile = __import__('io').BytesIO(body)
    handler.headers = {'Content-Length': str(len(body))}
    handler.path = "/api/review"
    handler._send_json = MagicMock()
    
    handler.do_POST()
    
    # the second arg to _write_json should be the mutated dictionary
    write_data = mock_write.call_args[0][1]
    assert "LIVE-001" in write_data
    assert write_data["LIVE-001"]["review"]["decision"] == "Edited"
    handler._send_json.assert_called_with(200, {"status": "saved"})

def test_oversized_payload():
    handler = NetSageHTTPRequestHandler(MockRequest(), client_address=('127.0.0.1', 8080), server=MockServer())
    # Faking a 2MB payload length header
    handler.rfile = __import__('io').BytesIO(b"")
    handler.headers = {'Content-Length': "2000000"}
    handler.path = "/api/diagnose"
    handler.send_error = MagicMock()
    
    handler.do_POST()
    
    handler.send_error.assert_called_with(413, "Payload Too Large")
