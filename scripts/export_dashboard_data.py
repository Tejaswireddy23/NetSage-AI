import pandas as pd
import json
from pathlib import Path

def export_data():
    cases = pd.read_csv('data/cases.csv')
    metadata_path = Path('data/case_metadata.csv')
    if metadata_path.exists():
        metadata = pd.read_csv(metadata_path).fillna('')
        cases = cases.merge(metadata, on='case_id', how='left')
    diag = pd.read_csv('runner/diagnosis_results.csv')
    review = pd.read_csv('review/review_template.csv')
    
    # Merge cases and diagnosis
    df = cases.merge(diag, on='case_id', how='left')
    
    # review_template has case_id, ai_root_cause, expected_fault, reviewer_decision, corrected_diagnosis, reviewer_notes, reviewer_name, review_date
    review_cols = ['case_id', 'reviewer_decision', 'corrected_diagnosis', 'reviewer_notes', 'reviewer_name', 'review_date']
    df = df.merge(review[review_cols], on='case_id', how='left')

    verification_path = Path('verification/verification_results.csv')
    if verification_path.exists():
        verification = pd.read_csv(verification_path).fillna('')
        # A case can have several commands; retain the most recently recorded row.
        if not verification.empty:
            verification = verification.drop_duplicates('case_id', keep='last')
            df = df.merge(verification, on='case_id', how='left')
    
    records = df.fillna("").to_dict(orient='records')
    with open('dashboard/src/data.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)
    print("Exported dashboard/src/data.json")

if __name__ == '__main__':
    export_data()
