import numpy as np
import pandas as pd
from typing import Dict, Any

FEATURE_NAMES = (
    [f"V{i}" for i in range(1, 29)] + 
    ["Amount", "amount_log", "amount_zscore", "hour_of_day", "day_of_week", 
     "sin_hour", "cos_hour", "tx_velocity_1h", "tx_velocity_6h", "tx_velocity_24h", "amount_sum_24h"]
)

def compute_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes temporal and behavioral risk features without target or future leakage.
    Sorts by 'Time' chronologically before computing rolling metrics.
    """
    df = df.copy()
    
    # Ensure sorted by Time to guarantee strict causal temporal ordering (t <= T)
    if not df['Time'].is_monotonic_increasing:
        df = df.sort_values('Time').reset_index(drop=True)

    # 1. Log Amount
    df['amount_log'] = np.log1p(np.maximum(df['Amount'], 0))

    # 2. Amount Z-score and Percentile
    amount_mean = df['Amount'].mean()
    amount_std = df['Amount'].std() + 1e-6
    df['amount_zscore'] = (df['Amount'] - amount_mean) / amount_std

    # 3. Cyclical Temporal Features (Time is in seconds elapsed)
    seconds_in_day = 86400.0
    time_of_day_sec = df['Time'] % seconds_in_day
    hour_of_day = time_of_day_sec / 3600.0
    
    df['hour_of_day'] = hour_of_day
    df['day_of_week'] = (df['Time'] // seconds_in_day) % 7
    
    # Radians for periodic sin/cos representation
    rad_hour = (hour_of_day / 24.0) * 2 * np.pi
    df['sin_hour'] = np.sin(rad_hour)
    df['cos_hour'] = np.cos(rad_hour)

    # 4. Rolling Window Velocities (Strictly <= current time T)
    # Using Time column (seconds) as temporal index
    times = df['Time'].values
    amounts = df['Amount'].values
    n = len(df)

    v1h = np.ones(n, dtype=int)
    v6h = np.ones(n, dtype=int)
    v24h = np.ones(n, dtype=int)
    sum24h = amounts.copy()

    # Efficient window search for large datasets
    # Find start indices for 1h (3600s), 6h (21600s), 24h (86400s)
    idx_1h = np.searchsorted(times, times - 3600, side='left')
    idx_6h = np.searchsorted(times, times - 21600, side='left')
    idx_24h = np.searchsorted(times, times - 86400, side='left')

    for i in range(n):
        v1h[i] = i - idx_1h[i] + 1
        v6h[i] = i - idx_6h[i] + 1
        v24h[i] = i - idx_24h[i] + 1
        sum24h[i] = amounts[idx_24h[i]:i+1].sum()

    df['tx_velocity_1h'] = v1h
    df['tx_velocity_6h'] = v6h
    df['tx_velocity_24h'] = v24h
    df['amount_sum_24h'] = sum24h

    return df

def extract_single_tx_features(amount: float, time_sec: float, pca_features: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Extracts features for a single real-time transaction input.
    """
    pca_dict = pca_features or {}
    for i in range(1, 29):
        col = f"V{i}"
        if col not in pca_dict:
            pca_dict[col] = 0.0 # Default centered PCA value if missing

    amount_log = float(np.log1p(max(amount, 0)))
    # Standard baseline statistics derived from training distribution (mean=88.35, std=250.12)
    amount_zscore = float((amount - 88.35) / 250.12)
    
    hour = float((time_sec % 86400.0) / 3600.0)
    day = float((time_sec // 86400.0) % 7)
    rad = (hour / 24.0) * 2 * np.pi
    
    feats = {
        **pca_dict,
        "Amount": amount,
        "amount_log": amount_log,
        "amount_zscore": amount_zscore,
        "hour_of_day": hour,
        "day_of_week": day,
        "sin_hour": float(np.sin(rad)),
        "cos_hour": float(np.cos(rad)),
        "tx_velocity_1h": 1,
        "tx_velocity_6h": 1,
        "tx_velocity_24h": 1,
        "amount_sum_24h": amount
    }
    return feats
