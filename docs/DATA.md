# SentinelRisk — Dataset & Feature Engineering Specifications

## Primary Benchmark Dataset

- **Name**: MLG-ULB Credit Card Fraud Detection Dataset
- **Source**: Kaggle / OpenML (Dataset #42175)
- **Total Rows**: 284,806
- **Fraud Labels (`Class = 1`)**: 492
- **Legitimate Labels (`Class = 0`)**: 284,314
- **Fraud Class Imbalance**: ~0.1727%

---

## Leakage Prevention Protocol

To prevent temporal data leakage:
1. All rolling window metrics (velocity 1h, 6h, 24h) use strict inequality $t \le T$.
2. Train (70%), Validation (15%), and Test (15%) splits are created purely chronologically without random shuffling.
3. Feature normalization (means and standard deviations) is calculated exclusively on training partitions.
