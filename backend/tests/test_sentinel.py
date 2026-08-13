import pytest
from fastapi.testclient import TestClient
import numpy as np
import pandas as pd

from backend.app.main import app
from backend.app.features import compute_temporal_features, extract_single_tx_features
from backend.app.rules import evaluate_deterministic_rules
from backend.app.scoring import probability_to_risk_score
from backend.app.decisions import evaluate_decision_policy
from backend.app.simulator import run_threshold_simulation
from backend.app.ingestion import load_and_validate_dataset

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "model_version" in data

def test_temporal_feature_engineering_no_leakage():
    # Construct mock dataset ordered chronologically
    df_raw = pd.DataFrame({
        "Time": [10.0, 50.0, 100.0, 3700.0, 90000.0],
        "Amount": [10.0, 200.0, 15.0, 500.0, 1200.0],
        "Class": [0, 0, 0, 1, 0]
    })
    for i in range(1, 29):
        df_raw[f"V{i}"] = 0.0

    df_feat = compute_temporal_features(df_raw)
    assert len(df_feat) == 5
    assert "amount_log" in df_feat.columns
    assert "tx_velocity_1h" in df_feat.columns
    
    # 1h velocity at idx 3 (3700s) relative to 3700s - 3600s = 100s -> idx 2 is 100s, so idx 2 & 3 are in 1h window -> 2 tx
    assert df_feat.iloc[3]["tx_velocity_1h"] == 2

def test_deterministic_rules():
    features = {"hour_of_day": 3.0, "tx_velocity_1h": 6, "V14": -6.5, "V12": -1.0}
    rules = evaluate_deterministic_rules(amount=3000.0, time_sec=10000.0, risk_score=85.0, features=features)
    
    rule_ids = [r["rule_id"] for r in rules]
    assert "RULE_EXTREME_AMOUNT" in rule_ids
    assert "RULE_HIGH_VELOCITY" in rule_ids
    assert "RULE_SCORE_BREACH" in rule_ids

def test_risk_scoring_and_decisions():
    # Low risk
    score, level = probability_to_risk_score(0.05)
    assert score == 5.0
    assert level == "LOW"
    decision, _, _ = evaluate_decision_policy(score, level, [])
    assert decision == "ALLOW"

    # High risk
    score, level = probability_to_risk_score(0.85)
    assert score == 85.0
    assert level == "CRITICAL"
    decision, _, _ = evaluate_decision_policy(score, level, [])
    assert decision == "BLOCK"

def test_single_transaction_scoring_api():
    payload = {
        "amount": 450.0,
        "time": 7200.0,
        "is_synthetic": True
    }
    response = client.post("/api/v1/transactions/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert data["decision"] in ["ALLOW", "CHALLENGE", "REVIEW", "BLOCK"]
    assert "top_signals" in data

def test_threshold_simulation_api():
    payload = {
        "threshold_allow": 20.0,
        "threshold_review": 75.0,
        "cost_false_positive": 50.0,
        "cost_missed_fraud": 100.0,
        "cost_manual_review": 15.0
    }
    response = client.post("/api/v1/simulate/threshold", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_transactions"] > 0
    assert "fraud_capture_rate" in data
    assert "total_financial_impact" in data

def test_monitoring_api():
    response = client.get("/api/v1/monitoring")
    assert response.status_code == 200
    data = response.json()
    assert data["total_scored_transactions"] > 0
    assert "risk_distribution" in data
