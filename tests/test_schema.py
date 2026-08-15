import pandas as pd
import pytest
import os

def test_schema_columns_and_categories():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cases.csv')
    df = pd.read_csv(csv_path)

    expected_columns = [
        'case_id', 'title', 'category', 'symptom', 'topology_note', 'show_outputs',
        'expected_fault', 'osi_layer', 'concept', 'severity', 'expected_next_command', 'expected_fix'
    ]

    # Check column names and order match exactly
    assert list(df.columns) == expected_columns, "Columns in cases.csv do not match schema"

    allowed_categories = {
        'VLAN', 'Gateway/IP', 'DHCP', 'DNS', 'Routing', 'ACL', 'NAT', 'Wireless'
    }

    # Check if category values are within the allowed set
    for category in df['category']:
        assert category in allowed_categories, f"Invalid category found: {category}"
