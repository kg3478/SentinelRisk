# SentinelRisk — REST API Reference Specification

## 1. Overview & Protocol Standards

The SentinelRisk REST API is engineered with **FastAPI 0.110+** and **Pydantic v2**, offering sub-20ms latency, strict type validation, and automatic OpenAPI schema generation.

- **Base URL**: `http://localhost:8000/api/v1`
- **Interactive Documentation**: Swagger UI at `http://localhost:8000/docs`, ReDoc at `http://localhost:8000/redoc`.
- **Content-Type**: `application/json`

---

## 2. API Endpoint Catalog

| Method | Endpoint | Description | SLA Target |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | System health check and active model version | $< 5\text{ ms}$ |
| `POST` | `/transactions/score` | Real-time single transaction evaluation | $< 20\text{ ms}$ |
| `POST` | `/transactions/batch-score` | High-throughput batch scoring | $< 50\text{ ms}$ |
| `GET` | `/transactions/{id}` | Retrieve transaction and decision details | $< 10\text{ ms}$ |
| `GET` | `/cases` | Query analyst investigation queue | $< 15\text{ ms}$ |
| `GET` | `/cases/{id}` | Fetch full case investigation dossier | $< 10\text{ ms}$ |
| `POST` | `/cases/{id}/override` | Submit human analyst decision override | $< 20\text{ ms}$ |
| `POST` | `/simulate/threshold` | Cost-sensitive threshold what-if simulation | $< 150\text{ ms}$ |
| `GET` | `/monitoring` | Population Stability Index (PSI) and system health | $< 15\text{ ms}$ |
| `GET` | `/metrics` | Active model evaluation metrics | $< 10\text{ ms}$ |
| `POST` | `/dataset/ingest` | Trigger dataset ingestion and validation | Background |
| `POST` | `/model/train` | Trigger end-to-end model retraining | Background |

---

## 3. Real-Time Scoring APIs

### 3.1 Score Single Transaction
`POST /api/v1/transactions/score`

Evaluates an incoming payment authorization payload through feature extraction, calibrated LightGBM scoring, deterministic safety rules, policy arbitration, and SHAP explainability.

#### Request Body (`TransactionCreate`):
```json
{
  "amount": 3800.00,
  "time": 54000.0,
  "pca_features": {
    "V1": -1.25,
    "V2": 2.10,
    "V12": -4.20,
    "V14": -5.80
  },
  "is_synthetic": false
}
```

#### Response Body (`TransactionScoreResponse`):
```json
{
  "transaction_id": "7f8b9a10-23c4-4b82-93de-87fa0192bd81",
  "external_tx_id": "TX-4F8A9C2E1B",
  "amount": 3800.00,
  "timestamp": "2026-10-04T15:30:00Z",
  "risk_score": 84.5,
  "risk_level": "CRITICAL",
  "calibrated_probability": 0.845,
  "model_version": "v1.0.0-lightgbm",
  "decision": "BLOCK",
  "confidence": 0.99,
  "triggered_rules": [
    {
      "rule_id": "RULE_EXTREME_AMOUNT",
      "rule_name": "Extreme Amount Anomaly",
      "severity": "HIGH",
      "evidence": {
        "amount": 3800.00,
        "threshold": 2500.0
      },
      "explanation": "Transaction amount of €3,800.00 exceeds the high-risk threshold of €2,500.00."
    },
    {
      "rule_id": "RULE_ANOMALOUS_PATTERN",
      "rule_name": "Anomalous Behavioral Pattern (PCA Breach)",
      "severity": "HIGH",
      "evidence": {
        "V14": -5.80,
        "V12": -4.20
      },
      "explanation": "Behavioral vector deviation detected on primary anomaly subspace features (V14/V12)."
    },
    {
      "rule_id": "RULE_SCORE_BREACH",
      "rule_name": "Critical Risk Score Breach",
      "severity": "CRITICAL",
      "evidence": {
        "risk_score": 84.5,
        "threshold": 75.0
      },
      "explanation": "Machine Learning calibrated risk score (84.5/100) breached critical safety threshold."
    }
  ],
  "top_signals": [
    {
      "feature_name": "V14",
      "contribution": 0.464,
      "direction": "POS_RISK",
      "description": "Behavioral vector deviation on V14 (-5.80) strongly contributed to risk estimation."
    },
    {
      "feature_name": "Amount",
      "contribution": 0.350,
      "direction": "POS_RISK",
      "description": "High transaction amount (€3,800.00) contributed positively to model risk score."
    }
  ],
  "reasons": [
    "Triggered Rule [Extreme Amount Anomaly]: Transaction amount of €3,800.00 exceeds the high-risk threshold of €2,500.00.",
    "Triggered Rule [Critical Risk Score Breach]: Machine Learning calibrated risk score (84.5/100) breached critical safety threshold.",
    "Risk Score (84.5/100) exceeded block policy threshold (75.0)."
  ],
  "case_created": true,
  "case_id": "2e8c1490-67df-48aa-b519-012ab988c5ef"
}
```

---

## 4. Case Management APIs

### 4.1 List Investigation Cases
`GET /api/v1/cases?status=NEW&limit=50`

#### Response:
```json
[
  {
    "id": "2e8c1490-67df-48aa-b519-012ab988c5ef",
    "case_number": "CASE-7D9A1C3F",
    "transaction_id": "7f8b9a10-23c4-4b82-93de-87fa0192bd81",
    "amount": 3800.00,
    "risk_score": 84.5,
    "original_decision": "BLOCK",
    "status": "NEW",
    "override_decision": null,
    "override_reason": null,
    "priority": "CRITICAL",
    "created_at": "2026-10-04T15:30:00Z",
    "updated_at": "2026-10-04T15:30:00Z"
  }
]
```

### 4.2 Submit Decision Override
`POST /api/v1/cases/{id}/override`

#### Request Body (`CaseOverrideRequest`):
```json
{
  "new_decision": "APPROVED",
  "reason": "Cardholder identity and high-value purchase verified via phone call. Verified legitimate false alarm."
}
```

#### Response:
```json
{
  "status": "SUCCESS",
  "case_id": "2e8c1490-67df-48aa-b519-012ab988c5ef",
  "new_status": "APPROVED"
}
```

---

## 5. Policy & Threshold Simulator API

### 5.1 Run Threshold Simulation
`POST /api/v1/simulate/threshold`

#### Request Body (`ThresholdSimulationRequest`):
```json
{
  "threshold_allow": 20.0,
  "threshold_review": 75.0,
  "cost_false_positive": 50.0,
  "cost_missed_fraud": 100.0,
  "cost_manual_review": 15.0
}
```

#### Response Body (`ThresholdSimulationResponse`):
```json
{
  "threshold_allow": 20.0,
  "threshold_review": 75.0,
  "total_transactions": 42722,
  "total_fraud_count": 52,
  "fraud_captured_count": 47,
  "fraud_capture_rate": 90.38,
  "false_positive_count": 358,
  "false_positive_rate": 0.8389,
  "approval_rate": 95.82,
  "review_rate": 3.32,
  "block_rate": 0.86,
  "estimated_fraud_loss": 2140.50,
  "estimated_false_positive_cost": 17900.00,
  "estimated_review_cost": 21150.00,
  "total_financial_impact": 41190.50,
  "recommendation": "Balanced threshold operating point. Fraud Capture Rate is 90.4% with FP Rate of 0.84%."
}
```

---

## 6. System Monitoring & Health APIs

### 6.1 System Health
`GET /api/v1/health`
```json
{
  "status": "HEALTHY",
  "timestamp": "2026-10-04T15:35:00Z",
  "model_version": "v1.0.0-lightgbm",
  "model_loaded": true,
  "environment": "production-ready"
}
```

### 6.2 Monitoring Metrics
`GET /api/v1/monitoring`
```json
{
  "total_scored_transactions": 284806,
  "fraud_rate_estimate": 0.1727,
  "avg_risk_score": 4.12,
  "risk_distribution": {
    "LOW": 272800,
    "MEDIUM": 8500,
    "HIGH": 2800,
    "CRITICAL": 706
  },
  "decision_breakdown": {
    "ALLOW": 272800,
    "CHALLENGE": 8500,
    "REVIEW": 2800,
    "BLOCK": 706
  },
  "active_model_version": "v1.0.0-lightgbm",
  "model_pr_auc": 0.8542,
  "model_brier_score": 0.0012,
  "psi_score_drift": 0.0182,
  "is_drifted": false,
  "system_latency_ms": 14.5
}
```
