import os
import json
import pytest
import pandas as pd
from unittest.mock import patch
from scripts import diagnose

MOCK_JSON_RESPONSE = """{
  "root_cause": "The issue is mock-diagnosed.",
  "confidence": 0.99,
  "osi_layer": "Layer 3 - Network",
  "evidence": [
    "Evidence line 1",
    "Evidence line 2"
  ],
  "next_command": "show ip route",
  "fix_steps": [
    "Step 1",
    "Step 2"
  ]
}"""

@pytest.fixture
def temp_diagnoses_file(tmp_path):
    d_file = tmp_path / "diagnoses.json"
    return str(d_file)

@pytest.fixture
def mock_dataset():
    # Use real cases.csv but only care about the formatting logic 
    df = pd.read_csv("data/cases.csv")
    return df

@patch("scripts.diagnose.call_llm")
def test_smoke_diagnose(mock_call_llm, mock_dataset, temp_diagnoses_file):
    # Setup mock return value
    mock_call_llm.return_value = MOCK_JSON_RESPONSE
    
    # Run the pipeline for case C-001
    diagnose.run_case("C-001", mock_dataset, output_path=temp_diagnoses_file)
    
    # 1. Verify a real network call was NOT made (mock was called)
    mock_call_llm.assert_called_once()
    
    prompt_sent = mock_call_llm.call_args[0][0]
    
    # 2. Verify prompt placeholders were replaced
    assert "{{SYMPTOM}}" not in prompt_sent
    assert "{{TOPOLOGY_NOTE}}" not in prompt_sent
    assert "{{SHOW_OUTPUTS}}" not in prompt_sent
    assert "{{RULE_FINDINGS}}" not in prompt_sent
    
    # 3. Verify exactly 6 rule findings were passed into the prompt
    # run_all returns 6 findings. Let's make sure the prompt sent includes "Rule: check_missing_route" etc.
    assert "Rule: check_duplicate_ip" in prompt_sent
    assert "Rule: check_missing_route" in prompt_sent
    assert "Rule: check_wrong_mask" in prompt_sent
    assert "Rule: check_gateway_mismatch" in prompt_sent
    assert "Rule: check_interface_down" in prompt_sent
    assert "Rule: check_missing_vlan" in prompt_sent
    
    # 4. Read the generated diagnoses.json
    assert os.path.exists(temp_diagnoses_file)
    with open(temp_diagnoses_file, "r") as f:
        data = json.load(f)
        
    # 5. Verify the key is correct
    assert "C-001" in data
    record = data["C-001"]
    
    # 6. Verify required outer fields
    assert "raw_response" in record
    assert "parsed_diagnosis" in record
    assert "prompt_version" in record
    assert "model" in record
    
    assert record["prompt_version"] == "v1"
    
    # 7. Verify parsed fields
    parsed = record["parsed_diagnosis"]
    assert set(parsed.keys()) == {
        "root_cause",
        "confidence",
        "osi_layer",
        "evidence",
        "next_command",
        "fix_steps"
    }
    
    # Ensure types mapped properly
    assert isinstance(parsed["confidence"], float)
    assert isinstance(parsed["evidence"], list)
    assert isinstance(parsed["fix_steps"], list)
    
    # 8. Ensure NO API keys are leaked (the file only has the schema)
    # The output should literally only be the JSON structure plus metadata.
    dump_str = json.dumps(data)
    # Generic safeguard assertion that our environment API key hasn't bled into the output
    from scripts.diagnose import load_environment
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        assert api_key not in dump_str
