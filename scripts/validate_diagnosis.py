import json
import jsonschema

DIAGNOSIS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "root_cause": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "osi_layer": {"type": "string"},
        "evidence": {
            "type": "array",
            "items": {"type": "string"}
        },
        "next_command": {"type": "string"},
        "fix_steps": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": [
        "root_cause",
        "confidence",
        "osi_layer",
        "evidence",
        "next_command",
        "fix_steps"
    ],
    "additionalProperties": False
}

def validate(raw_response: str) -> dict:
    """
    Validates a raw LLM response string against the strict TASK-006 schema.
    Returns the parsed dictionary if valid.
    Returns {"status": "validation_error", "error": "..."} if invalid.
    Does NOT auto-repair, add missing keys, clamp values, or raise exceptions to caller.
    """
    clean_json = raw_response.strip()
    if clean_json.startswith("```json"):
        clean_json = clean_json[7:]
    elif clean_json.startswith("```"):
        clean_json = clean_json[3:]
    if clean_json.endswith("```"):
        clean_json = clean_json[:-3]
    clean_json = clean_json.strip()

    try:
        data = json.loads(clean_json)
    except json.JSONDecodeError as e:
        return {"status": "validation_error", "error": f"JSON Decode Error: {str(e)}"}

    try:
        jsonschema.validate(instance=data, schema=DIAGNOSIS_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        return {"status": "validation_error", "error": f"Schema Validation Error: {str(e)}"}

    return data
