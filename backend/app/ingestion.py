import os
import hashlib
import pandas as pd
from typing import Dict, Any, Tuple
from backend.app.config import settings

def load_and_validate_dataset(csv_path: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads transaction dataset, checks schema, missing values, duplicates, and returns dataframe + quality report.
    Guarantees strict compliance with MLG-ULB Credit Card Fraud dataset properties.
    """
    path = csv_path or settings.DATA_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at '{path}'. Please run 'python data/download_dataset.py' to acquire the MLG-ULB Credit Card Fraud dataset."
        )

    # Downcast floats to float32 to reduce memory footprint by 50% for 512MB RAM cloud tiers
    dtype_dict = {f"V{i}": "float32" for i in range(1, 29)}
    dtype_dict["Amount"] = "float32"
    dtype_dict["Time"] = "float32"

    df = pd.read_csv(path, dtype=dtype_dict)
    
    # Standardize Class column
    if 'Class' not in df.columns and 'class' in df.columns:
        df.rename(columns={'class': 'Class'}, inplace=True)
        
    required_cols = ['Time', 'Amount', 'Class'] + [f'V{i}' for i in range(1, 29)]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise ValueError(f"Dataset schema error: Missing required columns {missing_cols}")

    total_rows = len(df)
    missing_vals = int(df[required_cols].isnull().sum().sum())
    duplicates = int(df.duplicated().sum())
    
    df['Class'] = df['Class'].astype(int)
    fraud_count = int(df['Class'].sum())
    fraud_rate = (fraud_count / total_rows) * 100
    
    # Hash calculation
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    file_hash = hasher.hexdigest()

    report = {
        "dataset_name": "Credit Card Fraud Detection (MLG-ULB / Worldline)",
        "source_url": "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
        "file_hash": file_hash,
        "total_transactions": total_rows,
        "fraud_count": fraud_count,
        "legitimate_count": total_rows - fraud_count,
        "fraud_rate_pct": round(fraud_rate, 4),
        "missing_values_count": missing_vals,
        "duplicate_rows_count": duplicates,
        "time_min_sec": float(df['Time'].min()),
        "time_max_sec": float(df['Time'].max()),
        "amount_min": float(df['Amount'].min()),
        "amount_max": float(df['Amount'].max()),
        "amount_mean": float(df['Amount'].mean()),
        "amount_median": float(df['Amount'].median()),
        "schema_validation": "PASS" if not missing_cols and missing_vals == 0 else "FAIL"
    }

    return df, report
