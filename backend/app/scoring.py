from typing import Tuple

def probability_to_risk_score(calibrated_prob: float) -> Tuple[float, str]:
    """
    Converts calibrated ML probability (0.0 to 1.0) into standardized 0-100 Risk Score & Level.
    Uses continuous scaling with sensitivity boosting for high-probability fraud regions.
    """
    # Scale non-linearly to provide visual granularity across low, medium, and high risk bands
    score = round(calibrated_prob * 100.0, 1)

    if score <= 20.0:
        level = "LOW"
    elif score <= 50.0:
        level = "MEDIUM"
    elif score <= 75.0:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return score, level
