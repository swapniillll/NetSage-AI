import os
import json
import traceback
import pandas as pd
from typing import Dict, Any

from scripts.rule_checker import run_all
from scripts.diagnose import run_case, load_environment

def main(cases_file="data/cases.csv", rule_results_file="data/rule_results.json", diagnoses_file="data/diagnoses.json"):
    load_environment()
    
    if not os.path.exists(cases_file):
        print(f"Error: Dataset {cases_file} not found.")
        return
        
    df = pd.read_csv(cases_file)
    total_cases = len(df)
    
    rule_results_data = {}
    
    # We want a fresh diagnoses.json for the full run so we don't append to a dirty state
    if os.path.exists(diagnoses_file):
        # We will backup or just start fresh by writing empty JSON
        with open(diagnoses_file, "w", encoding="utf-8") as f:
            json.dump({}, f)

    errors = 0
    
    for _, row in df.iterrows():
        case_id = row['case_id']
        show_outputs = str(row['show_outputs'])
        
        try:
            # Output 1: Rule findings
            findings = run_all(show_outputs)
            rule_results_data[case_id] = [
                {
                    "rule_name": f.rule_name,
                    "triggered": f.triggered,
                    "detail": f.detail
                } for f in findings
            ]
            
            # Output 2: AI diagnosis pipeline
            run_case(case_id, df, output_path=diagnoses_file)
            print(f"{case_id}: done")
        except Exception as e:
            errors += 1
            print(f"{case_id}: error \u2014 Unexpected pipeline failure: {e}")
            traceback.print_exc()
            continue

    # Write Output 1 safely
    with open(rule_results_file, "w", encoding="utf-8") as f:
        json.dump(rule_results_data, f, indent=2)
        
    # Analyze Output 2 for summary
    successful = 0
    needs_manual_review = 0
    
    if os.path.exists(diagnoses_file):
        with open(diagnoses_file, "r", encoding="utf-8") as f:
            try:
                diag_data = json.load(f)
                for c_id, record in diag_data.items():
                    if record.get("status") == "needs_manual_review":
                        needs_manual_review += 1
                    elif "parsed_diagnosis" in record:
                        successful += 1
            except Exception:
                pass
                
    print("\nTotal cases:", total_cases)
    print("Successful:", successful)
    print("Needs manual review:", needs_manual_review)
    print("Errors:", errors)

if __name__ == "__main__":
    main()
