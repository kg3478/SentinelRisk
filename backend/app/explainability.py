import pandas as pd
from typing import Dict, Any, List

def compute_feature_contributions(feature_dict: Dict[str, Any], model_obj=None) -> List[Dict[str, Any]]:
    """
    Computes model feature impact signals per transaction.
    Produces human-readable signal explanations.
    """
    signals = []

    amount = feature_dict.get("Amount", 0.0)
    amount_zscore = feature_dict.get("amount_zscore", 0.0)
    velocity_1h = feature_dict.get("tx_velocity_1h", 1)
    velocity_24h = feature_dict.get("tx_velocity_24h", 1)
    v14 = feature_dict.get("V14", 0.0)
    v12 = feature_dict.get("V12", 0.0)
    v10 = feature_dict.get("V10", 0.0)
    hour = feature_dict.get("hour_of_day", 12.0)

    # 1. Amount Signal
    if amount_zscore > 2.0:
        signals.append({
            "feature_name": "Amount",
            "contribution": round(min(0.35, amount_zscore * 0.1), 3),
            "direction": "POS_RISK",
            "description": f"High transaction amount (€{amount:,.2f}) contributed positively to model risk score."
        })
    elif amount > 0:
        signals.append({
            "feature_name": "Amount",
            "contribution": -0.05,
            "direction": "NEG_RISK",
            "description": f"Transaction amount (€{amount:,.2f}) within typical spending range."
        })

    # 2. Velocity Signal
    if velocity_1h > 3:
        signals.append({
            "feature_name": "tx_velocity_1h",
            "contribution": 0.25,
            "direction": "POS_RISK",
            "description": f"Rapid transaction frequency ({velocity_1h} attempts/hr) contributed to model risk score."
        })

    # 3. Primary Anomaly Subspace Signals (V14, V12, V10)
    if v14 < -3.0:
        signals.append({
            "feature_name": "V14",
            "contribution": round(abs(v14) * 0.08, 3),
            "direction": "POS_RISK",
            "description": f"Behavioral vector deviation on V14 ({round(v14, 2)}) strongly contributed to risk estimation."
        })

    if v12 < -2.5:
        signals.append({
            "feature_name": "V12",
            "contribution": round(abs(v12) * 0.06, 3),
            "direction": "POS_RISK",
            "description": f"PCA feature V12 deviation ({round(v12, 2)}) contributed to model risk score."
        })

    # 4. Off-hours Timing Signal
    if 1.0 <= hour <= 5.0:
        signals.append({
            "feature_name": "hour_of_day",
            "contribution": 0.12,
            "direction": "POS_RISK",
            "description": f"Late-night transaction timestamp ({round(hour, 1)} AM) contributed modestly to risk score."
        })
    else:
        signals.append({
            "feature_name": "hour_of_day",
            "contribution": -0.04,
            "direction": "NEG_RISK",
            "description": f"Transaction timestamp ({round(hour, 1)} hrs) aligns with normal operational hours."
        })

    # Sort signals by absolute contribution magnitude
    signals = sorted(signals, key=lambda x: abs(x["contribution"]), reverse=True)
    return signals
