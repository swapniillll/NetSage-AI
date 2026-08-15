import pandas as pd
import pytest

def test_review_log_structure():
    df_review = pd.read_csv('data/review_log.csv')
    df_cases = pd.read_csv('data/cases.csv')
    
    expected_columns = ['case_id', 'decision', 'corrected_fields', 'reason', 'reviewer']
    assert list(df_review.columns) == expected_columns, 'Columns do not match expected.'
    
    assert len(df_review) == len(df_cases)
    assert set(df_review['case_id']) == set(df_cases['case_id'])
    assert df_review['case_id'].is_unique
    
    valid_decisions = {'Accepted', 'Edited', 'Rejected'}
    assert set(df_review['decision'].unique()).issubset(valid_decisions)
    
    count_actionable = len(df_review[df_review['decision'].isin(['Edited', 'Rejected'])])
    assert count_actionable >= 5
    
    actionable_df = df_review[df_review['decision'].isin(['Edited', 'Rejected'])]
    assert actionable_df['reason'].isna().sum() == 0
    assert (actionable_df['reason'] != '').all()
    
    edited_df = df_review[df_review['decision'] == 'Edited']
    assert edited_df['corrected_fields'].isna().sum() == 0
    assert (edited_df['corrected_fields'] != '').all()
    
    dist = df_review['decision'].value_counts()
    assert dist.get('Accepted', 0) == 21
    assert dist.get('Edited', 0) == 7
    assert dist.get('Rejected', 0) == 2
