import numpy as np
import pandas as pd
from typing import Dict, Any
from backend.app.model import global_risk_engine
from backend.app.ingestion import load_and_validate_dataset
from backend.app.features import compute_temporal_features

def run_threshold_simulation(
    threshold_allow: float = 20.0,
    threshold_review: float = 75.0,
    cost_false_positive: float = 50.0,
    cost_missed_fraud: float = 100.0,
    cost_manual_review: float = 15.0
) -> Dict[str, Any]:
    """
    Executes cost-sensitive threshold what-if simulation on test partition of the real dataset.
    Calculates exact trade-off between missed fraud loss, false positive friction, and review operational cost.
    """
    # Load dataset and compute features
    df, _ = load_and_validate_dataset()
    df_feat = compute_temporal_features(df)

    # Use unseen test partition (last 15%)
    test_start = int(len(df_feat) * 0.85)
    df_test = df_feat.iloc[test_start:].copy()

    X_test = df_test[global_risk_engine.feature_names]
    y_test = df_test['Class'].astype(int).values
    amounts = df_test['Amount'].values

    # Get calibrated probabilities and risk scores (0-100)
    if not global_risk_engine.calibrator:
        if not global_risk_engine.load_model():
            global_risk_engine.train_pipeline(df)

    test_probs = global_risk_engine.calibrator.predict_proba(X_test)[:, 1]
    scores = np.round(test_probs * 100.0, 1)

    total_tx = len(df_test)
    total_fraud = int(y_test.sum())
    total_legit = total_tx - total_fraud

    # Simulate decisions based on thresholds
    # Score <= threshold_allow -> ALLOW
    # threshold_allow < Score < threshold_review -> REVIEW
    # Score >= threshold_review -> BLOCK

    allowed_mask = scores <= threshold_allow
    review_mask = (scores > threshold_allow) & (scores < threshold_review)
    blocked_mask = scores >= threshold_review

    # Outcomes
    # Missed fraud = Fraud transactions that were ALLOWED
    missed_fraud_mask = allowed_mask & (y_test == 1)
    missed_fraud_count = int(missed_fraud_mask.sum())
    missed_fraud_value = float(amounts[missed_fraud_mask].sum())

    # Captured fraud = Fraud transactions that were REVIEWED or BLOCKED
    captured_fraud_count = total_fraud - missed_fraud_count
    fraud_capture_rate = (captured_fraud_count / max(1, total_fraud)) * 100.0

    # False Positives = Legitimate transactions that were BLOCKED
    fp_mask = blocked_mask & (y_test == 0)
    fp_count = int(fp_mask.sum())
    fp_rate = (fp_count / max(1, total_legit)) * 100.0

    # Review Volume = Legitimate or Fraud transactions routed to REVIEW
    review_count = int(review_mask.sum())

    # Calculate Costs
    # 1. Missed Fraud Loss = Actual transaction amounts missed + Chargeback cost per incident
    loss_missed_fraud = missed_fraud_value + (missed_fraud_count * cost_missed_fraud)
    # 2. False Positive Friction Cost
    cost_fp_total = fp_count * cost_false_positive
    # 3. Manual Review Operational Cost
    cost_review_total = review_count * cost_manual_review

    total_cost = loss_missed_fraud + cost_fp_total + cost_review_total

    approval_rate = (allowed_mask.sum() / total_tx) * 100.0
    review_rate = (review_count / total_tx) * 100.0
    block_rate = (blocked_mask.sum() / total_tx) * 100.0

    # Recommendation heuristic
    if fp_rate > 5.0:
        rec = "High False Positive Rate. Consider raising the ALLOW threshold to reduce customer friction."
    elif fraud_capture_rate < 80.0:
        rec = "Low Fraud Capture Rate. Consider lowering the REVIEW/BLOCK threshold to catch more fraudulent attempts."
    else:
        rec = f"Balanced threshold operating point. Fraud Capture Rate is {fraud_capture_rate:.1f}% with FP Rate of {fp_rate:.2f}%."

    return {
        "threshold_allow": threshold_allow,
        "threshold_review": threshold_review,
        "total_transactions": total_tx,
        "total_fraud_count": total_fraud,
        "fraud_captured_count": captured_fraud_count,
        "fraud_capture_rate": round(fraud_capture_rate, 2),
        "false_positive_count": fp_count,
        "false_positive_rate": round(fp_rate, 4),
        "approval_rate": round(approval_rate, 2),
        "review_rate": round(review_rate, 2),
        "block_rate": round(block_rate, 2),
        "estimated_fraud_loss": round(loss_missed_fraud, 2),
        "estimated_false_positive_cost": round(cost_fp_total, 2),
        "estimated_review_cost": round(cost_review_total, 2),
        "total_financial_impact": round(total_cost, 2),
        "recommendation": rec
    }
