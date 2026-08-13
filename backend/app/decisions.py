from typing import List, Dict, Any, Tuple
from backend.app.config import settings

def evaluate_decision_policy(
    risk_score: float, 
    risk_level: str, 
    triggered_rules: List[Dict[str, Any]],
    threshold_allow: float = None,
    threshold_review: float = None
) -> Tuple[str, float, List[str]]:
    """
    Combines ML Risk Score, Triggered Deterministic Rules, and Business Policy Thresholds.
    Returns: (Decision, Confidence, List of Reason Strings)
    """
    allow_limit = threshold_allow if threshold_allow is not None else settings.THRESHOLD_ALLOW
    review_limit = threshold_review if threshold_review is not None else settings.THRESHOLD_REVIEW

    severities = [r["severity"] for r in triggered_rules]
    reasons = []

    # Check rule severity escalations
    has_critical_rule = "CRITICAL" in severities
    has_high_rule = "HIGH" in severities
    has_medium_rule = "MEDIUM" in severities

    for r in triggered_rules:
        reasons.append(f"Triggered Rule [{r['rule_name']}]: {r['explanation']}")

    # 1. Hard Block Policy (Score > review_limit OR Critical Rule OR Multiple High Rules)
    if risk_score >= review_limit or has_critical_rule or severities.count("HIGH") >= 2:
        decision = "BLOCK"
        confidence = min(0.99, 0.85 + (risk_score / 200.0))
        if risk_score >= review_limit:
            reasons.append(f"Risk Score ({risk_score}/100) exceeded block policy threshold ({review_limit}).")

    # 2. Manual Investigation Review Policy (50 < Score < 75 OR High Rule)
    elif risk_score > settings.THRESHOLD_CHALLENGE or has_high_rule:
        decision = "REVIEW"
        confidence = 0.90
        if risk_score > settings.THRESHOLD_CHALLENGE:
            reasons.append(f"Risk Score ({risk_score}/100) elevated into manual review range.")

    # 3. Step-up Challenge Policy (20 < Score <= 50 OR Medium Rule)
    elif risk_score > allow_limit or has_medium_rule:
        decision = "CHALLENGE"
        confidence = 0.92
        if risk_score > allow_limit:
            reasons.append(f"Risk Score ({risk_score}/100) requires multi-factor authorization challenge.")

    # 4. Standard Allow Policy
    else:
        decision = "ALLOW"
        confidence = 0.98
        reasons.append(f"Risk Score ({risk_score}/100) within normal low-risk tolerance band.")

    return decision, round(confidence, 2), reasons
