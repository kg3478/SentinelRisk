# SentinelRisk — Machine Learning Architecture & Calibration

## Model Progression

1. **Rule-Based Baseline**: Hardcoded threshold checks.
2. **Logistic Regression Baseline**: Linear probability estimator.
3. **Candidate Model**: LightGBM Gradient Boosted Decision Trees with `scale_pos_weight` class weighting.
4. **Calibration**: Sigmoidal Platt Scaling (`CalibratedClassifierCV`) mapping raw tree outputs to true probabilities.

---

## Evaluation Metrics

Given the 0.1727% class imbalance, model performance is evaluated using:
- **PR-AUC (Precision-Recall Area Under Curve)**: Primary optimization metric.
- **Brier Score**: Measures probability calibration quality ($E[(f_i - y_i)^2]$).
- **ROC-AUC**: Standard discrimination metric.
- **Precision & Recall @ Operating Threshold**.
