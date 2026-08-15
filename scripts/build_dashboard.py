import pandas as pd
import json
import matplotlib.pyplot as plt
import os

def build_dashboard():
    os.makedirs('dashboard', exist_ok=True)
    
    if not all(os.path.exists(f) for f in ['data/cases.csv', 'data/review_log.csv', 'data/rule_results.json']):
        print('Missing required source files.')
        return

    df_cases = pd.read_csv('data/cases.csv')
    df_review = pd.read_csv('data/review_log.csv')
    
    total_cases = len(df_cases)
    issue_type_distribution = df_cases['category'].value_counts().to_dict()
    severity_distribution = df_cases['severity'].value_counts().to_dict()
    
    review_decisions = df_review['decision'].value_counts().to_dict()
    accepted = review_decisions.get('Accepted', 0)
    edited = review_decisions.get('Edited', 0)
    rejected = review_decisions.get('Rejected', 0)
    
    agreement_rate = accepted / total_cases if total_cases > 0 else 0
    correction_rate = (edited + rejected) / total_cases if total_cases > 0 else 0
    
    with open('data/rule_results.json') as file:
        rules = json.load(file)
        
    rule_finding_counts = {
        'check_missing_route': 0,
        'check_wrong_mask': 0,
        'check_gateway_mismatch': 0,
        'check_duplicate_ip': 0,
        'check_missing_vlan': 0,
        'check_interface_down': 0
    }
    
    for case_id, rs in rules.items():
        for r in rs:
            rn = r.get('rule_name')
            if r.get('triggered') is True:
                if rn in rule_finding_counts:
                    rule_finding_counts[rn] += 1
                else:
                    rule_finding_counts[rn] = 1
                    
    dashboard_data = {
        'total_cases': total_cases,
        'issue_type_distribution': issue_type_distribution,
        'severity_distribution': severity_distribution,
        'review_decisions': review_decisions,
        'agreement_rate': agreement_rate,
        'correction_rate': correction_rate,
        'rule_finding_counts': rule_finding_counts
    }
    
    with open('dashboard/dashboard_data.json', 'w') as file:
        json.dump(dashboard_data, file, indent=4)
        
    plt.figure(figsize=(10, 6))
    categories = list(issue_type_distribution.keys())
    counts = list(issue_type_distribution.values())
    plt.bar(categories, counts, color='skyblue')
    plt.title('Issue Type Distribution')
    plt.xlabel('Category')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('dashboard/issue_distribution.png')
    plt.close()
    
    plt.figure(figsize=(8, 8))
    labels = list(review_decisions.keys())
    sizes = list(review_decisions.values())
    color_map = {'Accepted': '#4CAF50', 'Edited': '#FFC107', 'Rejected': '#F44336'}
    pie_colors = [color_map.get(l, '#999999') for l in labels]
    
    plt.pie(sizes, labels=labels, colors=pie_colors, autopct='%1.1f%%', startangle=140)
    plt.title('Review Agreement Rate')
    plt.tight_layout()
    plt.savefig('dashboard/agreement_rate.png')
    plt.close()
    
    print('Dashboard built successfully.')

if __name__ == '__main__':
    build_dashboard()
