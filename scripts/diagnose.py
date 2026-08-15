import argparse
import json
import os
import sys
import pandas as pd
from typing import Dict, Any

from dotenv import load_dotenv
from anthropic import Anthropic

# Add parent dir to path so we can import from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.rule_checker import run_all
from scripts.validate_diagnosis import validate

PROMPT_FILE = "prompts_ai/diagnose_prompt.md"
CASES_FILE = "data/cases.csv"
DIAGNOSES_FILE = "data/diagnoses.json"
PROMPT_VERSION = "v1"
MODEL_NAME = "claude-3-5-sonnet-20240620"

def load_environment():
    """Loads environment variables without hardcoding secrets."""
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("WARNING: ANTHROPIC_API_KEY environment variable is not set. Real API calls will fail.")
    return api_key

def format_findings(findings) -> str:
    """Convert rule_checker Finding objects into prompt-friendly text."""
    lines = []
    for f in findings:
        lines.append(f"Rule: {f.rule_name}")
        lines.append(f"Triggered: {f.triggered}")
        lines.append(f"Detail: {f.detail}\n")
    return "\n".join(lines).strip()

def build_prompt(symptom: str, topology_note: str, show_outputs: str, rule_findings: str) -> str:
    """Load the prompt template and replace placeholders."""
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_template = f.read()
    
    prompt = prompt_template.replace("{{SYMPTOM}}", symptom)
    prompt = prompt.replace("{{TOPOLOGY_NOTE}}", topology_note)
    prompt = prompt.replace("{{SHOW_OUTPUTS}}", show_outputs)
    prompt = prompt.replace("{{RULE_FINDINGS}}", rule_findings)
    
    return prompt

def call_llm(prompt_text: str, model: str) -> str:
    """Send the completed prompt to the configured LLM API using Anthropic client."""
    client = Anthropic() # picks up ANTHROPIC_API_KEY automatically
    
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        temperature=0.0,
        system="You are a senior network-engineer helper AI within the NetSage troubleshooting platform.",
        messages=[
            {"role": "user", "content": prompt_text}
        ]
    )
    return response.content[0].text

def run_case(case_id: str, df: pd.DataFrame, output_path: str = DIAGNOSES_FILE):
    """Run the complete pipeline for a single case and save the result."""
    print(f"Processing case: {case_id}...")
    
    row = df[df['case_id'] == case_id]
    if row.empty:
        print(f"Error: Case {case_id} not found in {CASES_FILE}.")
        sys.exit(1)
        
    case_data = row.iloc[0]
    show_outputs = str(case_data['show_outputs'])
    symptom = str(case_data['symptom'])
    topology_note = str(case_data['topology_note'])
    
    # 3. Call rule checker
    findings = run_all(show_outputs)
    
    # 4. Format findings
    rule_findings = format_findings(findings)
    
    # 5 & 6. Build prompt
    prompt_text = build_prompt(symptom, topology_note, show_outputs, rule_findings)
    
    # 7 & 8. Call LLM
    try:
        raw_response = call_llm(prompt_text, MODEL_NAME)
    except Exception as e:
        print(f"LLM API Call failed for {case_id}: {e}")
        return
        
    # 9. JSON Validation and Single Retry logic
    parsed_data = validate(raw_response)
    
    if parsed_data.get("status") == "validation_error":
        print(f"Validation failed for {case_id}. Attempting exactly ONE retry...")
        retry_prompt = prompt_text + "\n\nCRITICAL: your last response was invalid JSON — return only valid JSON matching the schema."
        try:
            raw_response_2 = call_llm(retry_prompt, MODEL_NAME)
        except Exception as e:
            print(f"LLM API Call failed for {case_id} during retry: {e}")
            return
            
        parsed_data = validate(raw_response_2)
        
        if parsed_data.get("status") == "validation_error":
            print(f"Second validation failed for {case_id}. Saving for manual review.")
            record = {
                "case_id": case_id,
                "status": "needs_manual_review",
                "raw_response": raw_response_2
            }
        else:
            record = {
                "raw_response": raw_response_2,
                "parsed_diagnosis": parsed_data,
                "prompt_version": PROMPT_VERSION,
                "model": MODEL_NAME
            }
    else:
        record = {
            "raw_response": raw_response,
            "parsed_diagnosis": parsed_data,
            "prompt_version": PROMPT_VERSION,
            "model": MODEL_NAME
        }
    
    # 10. Save to diagnoses.json
    
    # Load existing to append/update
    diagnoses = {}
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                diagnoses = json.load(f)
            except json.JSONDecodeError:
                diagnoses = {}
                
    diagnoses[case_id] = record
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(diagnoses, f, indent=2)
        
    print(f"Success. Diagnosis saved for {case_id}.")

def main():
    parser = argparse.ArgumentParser(description="NetSage AI Diagnosis Pipeline Script")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--case", type=str, help="Single case ID to process (e.g., C-001)")
    group.add_argument("--all", action="store_true", help="Run against all cases in the dataset")
    
    args = parser.parse_args()
    
    load_environment()
    
    if not os.path.exists(CASES_FILE):
        print(f"Error: Dataset {CASES_FILE} not found.")
        sys.exit(1)
        
    df = pd.read_csv(CASES_FILE)
    
    if args.case:
        run_case(args.case, df)
    elif args.all:
        for case_id in df['case_id']:
            run_case(case_id, df)

if __name__ == "__main__":
    main()
