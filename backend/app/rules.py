from typing import Dict, Any, List

def evaluate_deterministic_rules(amount: float, time_sec: float, risk_score: float, features: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluates versioned deterministic risk rules against transaction context and features.
    Returns list of triggered rules with evidence and severity.
    """
    triggered_rules = []
    
    hour = features.get("hour_of_day", (time_sec % 86400.0) / 3600.0)
    velocity_1h = features.get("tx_velocity_1h", 1)
    v14 = features.get("V14", 0.0)
    v12 = features.get("V12", 0.0)

    # Rule 1: High Transaction Amount Anomaly
    if amount >= 2500.0:
        triggered_rules.append({
            "rule_id": "RULE_EXTREME_AMOUNT",
            "rule_name": "Extreme Amount Anomaly",
            "severity": "HIGH",
            "evidence": {"amount": amount, "threshold": 2500.0},
            "explanation": f"Transaction amount of €{amount:,.2f} exceeds the high-risk threshold of €2,500.00."
        })

    # Rule 2: High Velocity Spike
    if velocity_1h >= 5:
        triggered_rules.append({
            "rule_id": "RULE_HIGH_VELOCITY",
            "rule_name": "High Transaction Velocity Spike",
            "severity": "HIGH",
            "evidence": {"velocity_1h": velocity_1h, "threshold": 5},
            "explanation": f"Detected {velocity_1h} transactions within a 1-hour rolling window."
        })

    # Rule 3: Late Night High Value
    if 1.0 <= hour <= 5.0 and amount > 500.0:
        triggered_rules.append({
            "rule_id": "RULE_NIGHT_HIGH_VALUE",
            "rule_name": "Off-Hours High Value Transaction",
            "severity": "MEDIUM",
            "evidence": {"hour_of_day": round(hour, 2), "amount": amount},
            "explanation": f"High value transaction of €{amount:,.2f} initiated during off-hours ({round(hour, 1)} AM)."
        })

    # Rule 4: PCA Component Anomaly (V14 / V12 Signal Breach)
    if v14 < -5.0 or v12 < -4.0:
        triggered_rules.append({
            "rule_id": "RULE_ANOMALOUS_PATTERN",
            "rule_name": "Anomalous Behavioral Pattern (PCA Breach)",
            "severity": "HIGH",
            "evidence": {"V14": round(v14, 3), "V12": round(v12, 3)},
            "explanation": "Behavioral vector deviation detected on primary anomaly subspace features (V14/V12)."
        })

    # Rule 5: Critical Risk Score Breach
    if risk_score >= 75.0:
        triggered_rules.append({
            "rule_id": "RULE_SCORE_BREACH",
            "rule_name": "Critical Risk Score Breach",
            "severity": "CRITICAL",
            "evidence": {"risk_score": round(risk_score, 1), "threshold": 75.0},
            "explanation": f"Machine Learning calibrated risk score ({round(risk_score, 1)}/100) breached critical safety threshold."
        })

    return triggered_rules
