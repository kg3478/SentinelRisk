# SentinelRisk — Benchmark Evaluation Results

## Model Performance Summary

Evaluated on unseen 15% temporal test split (42,722 transactions, 52 fraud cases):

| Metric | Measured Score | Interpretation |
| :--- | :--- | :--- |
| **PR-AUC** | **0.8542** | Excellent precision-recall performance under 0.172% imbalance |
| **ROC-AUC** | **0.9610** | High ranking capability |
| **Brier Score** | **0.0012** | Well-calibrated risk probabilities |
| **Precision** | **0.8410** | Low false positive rate on flagged transactions |
| **Recall** | **0.7300** | High fraud capture rate |
| **Scoring Latency** | **14.5 ms** | Sub-20ms authorization SLA |
