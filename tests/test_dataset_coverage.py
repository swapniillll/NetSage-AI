import pandas as pd
import pytest
import os


def test_row_count_at_least_30():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cases.csv')
    df = pd.read_csv(csv_path)
    assert len(df) >= 30, f"Expected at least 30 rows, got {len(df)}"


def test_category_distribution():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cases.csv')
    df = pd.read_csv(csv_path)
    counts = df['category'].value_counts()

    required = {
        'VLAN': 5,
        'Gateway/IP': 5,
        'DHCP': 4,
        'DNS': 3,
        'Routing': 5,
        'ACL': 4,
        'NAT': 2,
        'Wireless': 2,
    }

    for category, minimum in required.items():
        actual = counts.get(category, 0)
        assert actual >= minimum, (
            f"Category '{category}' has {actual} cases, need at least {minimum}"
        )


def test_no_duplicate_case_ids():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cases.csv')
    df = pd.read_csv(csv_path)
    assert df['case_id'].nunique() == len(df), "Duplicate case_id values found"
