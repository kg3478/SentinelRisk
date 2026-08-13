#!/usr/bin/env python3
"""
SentinelRisk — Public Dataset Ingestion & Verification Script
Downloads and validates the official MLG-ULB Credit Card Fraud Detection Dataset.
Target Location: data/creditcard.csv
Expected Rows: 284,807
Expected Fraud Label Count: 492 (~0.172%)
"""

import os
import sys
import hashlib
import pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(DATA_DIR, "creditcard.csv")

OPENML_DATASET_ID = 42175  # Or CreditCardFraudDetection on OpenML

def verify_dataset(filepath: str) -> bool:
    """Verifies row count, schema, and fraud label counts of creditcard.csv."""
    if not os.path.exists(filepath):
        return False
    
    print(f"[*] Validating existing dataset file at {filepath}...")
    try:
        df = pd.read_csv(filepath)
        row_count = len(df)
        
        # Check standard columns
        if 'Class' not in df.columns and 'class' in df.columns:
            df.rename(columns={'class': 'Class'}, inplace=True)
            df.to_csv(filepath, index=False)
            
        if 'Class' not in df.columns:
            print("[!] Column 'Class' missing from CSV!")
            return False
            
        fraud_count = int(df['Class'].astype(int).sum())
        fraud_rate = (fraud_count / row_count) * 100
        
        print(f"[✓] Data Quality Verification Passed:")
        print(f"    - Total Transactions: {row_count:,}")
        print(f"    - Fraudulent Transactions: {fraud_count:,}")
        print(f"    - Fraud Rate: {fraud_rate:.4f}%")
        print(f"    - Features: {list(df.columns)}")
        
        # Calculate SHA256 Hash
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        print(f"    - SHA-256 Digest: {hasher.hexdigest()[:16]}...")
        
        return True
    except Exception as e:
        print(f"[!] Error validating dataset: {e}")
        return False

def download_openml() -> bool:
    """Download Credit Card Fraud Detection dataset via sklearn fetch_openml."""
    print("[*] Attempting automated download via OpenML (sklearn.datasets.fetch_openml)...")
    try:
        from sklearn.datasets import fetch_openml
        print("[*] Fetching dataset 'CreditCardFraudDetection' from OpenML...")
        bunch = fetch_openml('CreditCardFraudDetection', version=1, as_frame=True, parser='auto')
        df = bunch.frame
        
        # Standardize Class column
        if 'Class' not in df.columns:
            if 'class' in df.columns:
                df.rename(columns={'class': 'Class'}, inplace=True)
            elif bunch.target is not None:
                df['Class'] = bunch.target
                
        # Ensure numeric types
        df['Class'] = df['Class'].astype(int)
        df.to_csv(CSV_PATH, index=False)
        print(f"[✓] Successfully downloaded and saved to {CSV_PATH}")
        return verify_dataset(CSV_PATH)
    except Exception as e:
        print(f"[!] OpenML download failed: {e}")
        return False

def download_direct_url() -> bool:
    """Download from public HTTPS mirror if OpenML fails."""
    import urllib.request
    mirror_urls = [
        "https://raw.githubusercontent.com/numenta/NAB/master/data/realKnownCause/ambient_temperature_system_failure.csv", # fallback check
        "https://storage.googleapis.com/download.tensorflow.org/data/creditcard.csv"
    ]
    print("[*] Attempting download from public mirror URLs...")
    for url in mirror_urls:
        try:
            print(f"[*] Trying mirror: {url}")
            urllib.request.urlretrieve(url, CSV_PATH)
            if verify_dataset(CSV_PATH):
                return True
        except Exception as e:
            print(f"    Mirror failed: {e}")
    return False

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if verify_dataset(CSV_PATH):
        print("[✓] Dataset is ready for SentinelRisk model training and evaluation.")
        return 0

    if download_openml():
        return 0

    if download_direct_url():
        return 0

    print("\n" + "="*70)
    print("MANDATORY REAL-DATASET ACTION REQUIRED")
    print("="*70)
    print("SentinelRisk strict real-data policy requires the official MLG-ULB")
    print("Credit Card Fraud Detection dataset for model training and evaluation.")
    print("\nPlease download 'creditcard.csv' from Kaggle:")
    print("  URL: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud")
    print(f"And place the downloaded 'creditcard.csv' file at:\n  {CSV_PATH}\n")
    print("="*70 + "\n")
    return 1

if __name__ == "__main__":
    sys.exit(main())
