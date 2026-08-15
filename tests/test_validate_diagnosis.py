import json
import pytest
from scripts.validate_diagnosis import validate

def test_validate_valid_json():
    # TEST 1 - VALID
    valid_json = """{
        "root_cause": "The interface is down.",
        "confidence": 0.95,
        "osi_layer": "Layer 1",
        "evidence": ["show ip int brief says administratively down"],
        "next_command": "no shutdown",
        "fix_steps": ["Enter config mode", "Run no shutdown"]
    }"""
    result = validate(valid_json)
    # Must not contain "status" returning an error
    assert "status" not in result or result.get("status") != "validation_error"
    assert result["root_cause"] == "The interface is down."
    assert result["confidence"] == 0.95
    assert isinstance(result["evidence"], list)

def test_validate_malformed_json():
    # TEST 2 - MALFORMED
    bad_json = """{ "root_cause": "Missing brackets..."""
    result = validate(bad_json)
    assert result.get("status") == "validation_error"
    assert "JSON Decode Error" in result.get("error")

def test_validate_missing_field():
    missing_json = """{
        "root_cause": "Missing confidence",
        "osi_layer": "Layer 1",
        "evidence": ["ev"],
        "next_command": "cmd",
        "fix_steps": ["step"]
    }"""
    result = validate(missing_json)
    assert result.get("status") == "validation_error"
    assert "Schema Validation Error" in result.get("error")

def test_validate_confidence_too_high():
    bad_conf = """{
        "root_cause": "Test",
        "confidence": 1.5,
        "osi_layer": "Layer 1",
        "evidence": ["ev"],
        "next_command": "cmd",
        "fix_steps": ["step"]
    }"""
    result = validate(bad_conf)
    assert result.get("status") == "validation_error"
    assert "Schema Validation Error" in result.get("error")

def test_validate_confidence_too_low():
    bad_conf = """{
        "root_cause": "Test",
        "confidence": -0.1,
        "osi_layer": "Layer 1",
        "evidence": ["ev"],
        "next_command": "cmd",
        "fix_steps": ["step"]
    }"""
    result = validate(bad_conf)
    assert result.get("status") == "validation_error"

def test_validate_extra_fields():
    extra_field = """{
        "root_cause": "Test",
        "confidence": 0.5,
        "osi_layer": "Layer 1",
        "evidence": ["ev"],
        "next_command": "cmd",
        "fix_steps": ["step"],
        "invented_field": "unwanted"
    }"""
    result = validate(extra_field)
    assert result.get("status") == "validation_error"

def test_validate_wrong_type():
    wrong_type = """{
        "root_cause": "Test",
        "confidence": "should be float",
        "osi_layer": "Layer 1",
        "evidence": ["ev"],
        "next_command": "cmd",
        "fix_steps": ["step"]
    }"""
    result = validate(wrong_type)
    assert result.get("status") == "validation_error"
