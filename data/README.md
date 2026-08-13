# SentinelRisk — Dataset Provenance & Specifications

## Overview

SentinelRisk uses the **Credit Card Fraud Detection** dataset published by the **Machine Learning Group — ULB (Université Libre de Bruxelles) & Worldline collaboration**.

- **Source**: [Kaggle MLG-ULB Credit Card Fraud Dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- **OpenML Reference**: [OpenML Dataset #42175 / #1597](https://www.openml.org/d/42175)
- **License**: Database Contents License (DbCL) v1.0 / Open Data Commons

---

## Dataset Characteristics

- **Total Transactions**: 284,807
- **Fraudulent Transactions (`Class = 1`)**: 492
- **Legitimate Transactions (`Class = 0`)**: 284,315
- **Fraud Rate**: ~0.1727% (Extreme Class Imbalance)
- **Time Span**: 48 hours (172,792 seconds) of European cardholder transactions in September 2013

---

## Schema

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `Time` | Float / Int | Seconds elapsed between this transaction and the first transaction in the dataset |
| `V1` – `V28` | Float | Principal Components obtained via PCA transformation (anonymized feature vectors) |
| `Amount` | Float | Transaction amount in Euros |
| `Class` | Integer (0 or 1) | Ground-truth fraud label (1 = Fraudulent, 0 = Legitimate) |

---

## Compliance & Privacy Policy

> [!IMPORTANT]
> **Public Research Benchmark Notice**:
> This dataset contains anonymized research benchmark data. It does **not** represent live streaming production data from any bank, card network (Visa/Mastercard), or payment provider (Stripe, Paytm, PayPal).
> 
> SentinelRisk uses this real public dataset for model development, calibration, threshold optimization, and reproducible evaluation.
