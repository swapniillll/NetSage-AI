import pandas as pd
import re
import os

def test_responsible_ai_log():
    # 1. Read data/review_log.csv
    df_rev = pd.read_csv("data/review_log.csv")
    
    # 2. Read docs/responsible_ai_log.md
    with open("docs/responsible_ai_log.md", "r") as f:
        md_content = f.read()
        
    # 3. Extract case IDs from the markdown
    # The format is ## C-001 — Edited
    case_id_pattern = re.compile(r"## (C-\d{3}) — (Edited|Rejected)")
    matches = case_id_pattern.findall(md_content)
    extracted_case_ids = [m[0] for m in matches]
    
    # 4. Confirm at least 5 DISTINCT corrected case IDs are documented
    distinct_ids = set(extracted_case_ids)
    assert len(distinct_ids) >= 5, f"Expected at least 5 distinct cases, found {len(distinct_ids)}"
    
    # 5. Confirm every documented case ID exists in review_log.csv
    csv_cases_set = set(df_rev["case_id"])
    for cid in distinct_ids:
        assert cid in csv_cases_set, f"Documented case {cid} not found in review_log.csv"
        
    # 6. Confirm every documented case has decision Edited or Rejected
    for match in matches:
        cid, dec = match[0], match[1]
        actual_dec = df_rev[df_rev["case_id"] == cid]["decision"].values[0]
        assert actual_dec in ["Edited", "Rejected"], f"Documented case {cid} has decision {actual_dec}"
        assert dec == actual_dec, f"Documented decision mismatch for {cid}"
        
    # 7. Confirm the document contains the required section labels for each documented case
    required_labels = [
        "**AI diagnosis:**",
        "**Review classification:**",
        "**What was wrong:**",
        "**Corrected/final diagnosis:**",
        "**Why this matters:**"
    ]
    
    for label in required_labels:
        # Check that the label appears at least as many times as the distinct cases
        assert md_content.count(label) >= len(distinct_ids), f"Required label '{label}' is missing or insufficient."

