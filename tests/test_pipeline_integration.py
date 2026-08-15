import os
import json
import pytest
import pandas as pd
from unittest.mock import patch

from scripts import run_pipeline
from scripts import diagnose

MOCK_JSON_RESPONSE = """{
  "root_cause": "Test Issue",
  "confidence": 0.85,
  "osi_layer": "Layer 3 - Network",
  "evidence": ["Some proof"],
  "next_command": "show interfaces",
  "fix_steps": ["step A", "step B"]
}"""

@pytest.fixture
def temp_cases_file(tmp_path):
    f = tmp_path / "cases.csv"
    actual_df = pd.read_csv("data/cases.csv")
    test_df = actual_df.head(5).copy()
    test_df.to_csv(f, index=False)
    return str(f)

@pytest.fixture
def temp_rule_results(tmp_path):
    return str(tmp_path / "rule_results.json")

@pytest.fixture
def temp_diagnoses(tmp_path):
    return str(tmp_path / "diagnoses.json")

@patch("scripts.diagnose.call_llm")
def test_pipeline_integration(mock_call_llm, temp_cases_file, temp_rule_results, temp_diagnoses):
    
    # Setup LLM response sequence
    # C-001: Success
    # C-002: Success 
    # C-003: Manual Review (First invalid, second invalid)
    # C-004: Success (First invalid, second valid)
    # C-005: Simulating a hard code exception in run_case to test pipeline continuation
    
    call_returns = [
        MOCK_JSON_RESPONSE, # C-001 call 1
        MOCK_JSON_RESPONSE, # C-002 call 1
        "bad 1",            # C-003 call 1
        "bad 2",            # C-003 call 2
        "bad 1",            # C-004 call 1
        MOCK_JSON_RESPONSE, # C-004 call 2
        # C-005 will crash before LLM is successfully processed, so no more calls needed
    ]
    
    def side_effect_mock(*args, **kwargs):
        if len(call_returns) > 0:
            return call_returns.pop(0)
        return MOCK_JSON_RESPONSE
        
    mock_call_llm.side_effect = side_effect_mock
    
    original_run_case = diagnose.run_case
    
    def mock_run_case(case_id, df, output_path):
        if case_id == "C-005":
            raise Exception("Mocked unexpected crash")
        return original_run_case(case_id, df, output_path)
        
    with patch("scripts.run_pipeline.run_case", side_effect=mock_run_case), \
         patch("scripts.run_pipeline.load_environment"):
        
        # Run the orchestrator
        run_pipeline.main(
            cases_file=temp_cases_file,
            rule_results_file=temp_rule_results,
            diagnoses_file=temp_diagnoses
        )
        
    # 1. rule_results.json is created
    assert os.path.exists(temp_rule_results)
    with open(temp_rule_results, "r") as f:
        rule_data = json.load(f)
        
    # 3. Exactly 5 case IDs are represented in rule defaults
    assert len(rule_data.keys()) == 5
    assert "C-005" in rule_data # Proves it didn't crash C-005 rule calculation which happens before the exception
    
    # 4. Every case has 6 findings
    for case_id, res in rule_data.items():
        assert isinstance(res, list)
        assert len(res) == 6
        assert "rule_name" in res[0]
        
    # 2. diagnoses.json is created
    assert os.path.exists(temp_diagnoses)
    with open(temp_diagnoses, "r") as f:
        diag_data = json.load(f)
        
    # Diagnoses should only have 4 (since C-005 crashed unexpectedly)
    assert len(diag_data.keys()) == 4
    assert set(diag_data.keys()) == {"C-001", "C-002", "C-003", "C-004"}
    
    # 5. Case outputs match
    # C-001, C-002, C-004 should have parsed_diagnosis
    assert "parsed_diagnosis" in diag_data["C-001"]
    assert "parsed_diagnosis" in diag_data["C-002"]
    assert "parsed_diagnosis" in diag_data["C-004"]
    
    # C-003 should be needs_manual_review
    assert diag_data["C-003"]["status"] == "needs_manual_review"
    assert diag_data["C-003"]["raw_response"] == "bad 2"
