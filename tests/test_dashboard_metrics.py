import pandas as pd
import json
import os
import pytest

def test_dashboard_metrics():
    # Load dashboard data
    with open('dashboard/dashboard_data.json') as f:
        dash = json.load(f)
        
    df_cases = pd.read_csv('data/cases.csv')
    df_review = pd.read_csv('data/review_log.csv')
    with open('data/rule_results.json') as f:
        rules = json.load(f)
        
    # Test total cases
    assert dash['total_cases'] == len(df_cases)
    
    # Test category distribution
    cat_counts = df_cases['category'].value_counts().to_dict()
    assert dash['issue_type_distribution'] == cat_counts
    
    # Test review decisions
    rev_counts = df_review['decision'].value_counts().to_dict()
    assert dash['review_decisions'] == rev_counts
    
    # Test agreement rate
    expected_agreement = rev_counts.get('Accepted', 0) / len(df_cases)
    assert pytest.approx(dash['agreement_rate']) == expected_agreement
    
    # Test rule triggers
    t_counts = {
        'check_missing_route': 0, 'check_wrong_mask': 0, 'check_gateway_mismatch': 0,
        'check_duplicate_ip': 0, 'check_missing_vlan': 0, 'check_interface_down': 0
    }
    for rs in rules.values():
        for r in rs:
            if r.get('triggered') is True:
                rn = r.get('rule_name')
                if rn in t_counts:
                    t_counts[rn] += 1
                else:
                    t_counts[rn] = 1
    assert dash['rule_finding_counts'] == t_counts
