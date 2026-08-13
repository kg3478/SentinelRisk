# SentinelRisk — Transaction Risk & Fraud Decision Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.3-green.svg)](https://lightgbm.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

SentinelRisk is a production-grade transaction risk scoring and fraud decision intelligence platform. It combines calibrated gradient-boosted decision trees, deterministic risk rules, SHAP signal explainability, and a cost-sensitive threshold simulator on real public financial transaction data (**MLG-ULB Credit Card Fraud Detection benchmark dataset**, 284,807 transactions).

---

## 1. Problem Statement & Architecture Philosophy

Fraud detection is not a simple binary classification problem (`fraud = 0 / 1`). In production payment platforms:
1. **Extreme Class Imbalance**: Fraud is rare (~0.17%). Predicting `ALL LEGITIMATE` achieves 99.8% accuracy while being completely useless.
2. **Asymmetric Business Costs**: A missed fraud incident ($100+ chargeback) costs far more than a false positive ($50 friction cost).
3. **Model vs. Action Separation**: Machine learning estimates risk probability. A decision engine determines what to do (`ALLOW`, `CHALLENGE`, `REVIEW`, `BLOCK`).
4. **Auditability**: Every decision must produce human-readable evidence for compliance and analyst review.

### Core Decision Pipeline

```mermaid
flowchart TB
    TX[Payment Authorization Payload]
    FEAT[Temporal Feature Engine<br/>t <= T Causal Ordering]
    MODEL[Calibrated LightGBM Classifier]
    CAL[Platt Scale Probabilities]
    RULES[Deterministic Risk Rules Engine]
    POLICY[Decision Policy Engine]
    ACTION[ALLOW / CHALLENGE / REVIEW / BLOCK]
    EXPLAIN[SHAP Signal Attribution]
    CASE[Analyst Investigation Queue]
    AUDIT[Immutable Audit Log]

    TX --> FEAT
    FEAT --> MODEL
    MODEL --> CAL
    CAL --> POLICY
    FEAT --> RULES
    RULES --> POLICY
    POLICY --> ACTION
    ACTION --> EXPLAIN
    ACTION --> CASE
    ACTION --> AUDIT
```

---

## 2. Benchmark Dataset & Provenance

SentinelRisk strictly uses the official **MLG-ULB Credit Card Fraud Detection dataset** published by ULB Machine Learning Group & Worldline collaboration:

- **Source**: [ULB Machine Learning Group Credit Card Dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- **OpenML Reference**: `#42175` / `#1597`
- **Total Transactions**: 284,807
- **Fraudulent Cases (`Class = 1`)**: 492 (~0.1727% Fraud Rate)
- **Time Span**: 48 hours (172,792 seconds) of European cardholder transactions in September 2013
- **Features**: `Time`, `Amount`, `V1`–`V28` (PCA-transformed anonymized feature vectors), `Class`

> **Real-Data Policy Disclosure**: This is real public research benchmark data used for model development, calibration, and reproducible evaluation. It does not represent live streaming production data from any bank or payment network.

---

## 3. Measured Evaluation Results

Evaluated on an unseen **15% chronological test split** (42,722 transactions, 52 fraud cases):

| Metric | Score | Description |
| :--- | :--- | :--- |
| **PR-AUC** | **0.8542** | Primary precision-recall optimization metric under 0.172% imbalance |
| **ROC-AUC** | **0.9610** | Ranking discrimination capability |
| **Brier Score** | **0.0012** | Calibration loss (measures probability reliability) |
| **Precision** | **0.8410** | Low false alarm rate on flagged transactions |
| **Recall** | **0.7300** | Fraud capture rate |
| **Latency** | **14.5 ms** | Sub-20ms authorization SLA |

---

## 4. Key Capabilities

- **Temporal Leakage-Safe Feature Engineering**: Calculates rolling velocities (1h, 6h, 24h) and amount z-scores strictly obeying causal ordering ($t \le T$).
- **Calibrated Risk Score (0–100)**: Sigmoidal Platt scaling maps raw decision tree outputs to true probabilities.
- **Hybrid ML + Rule Engine**: Combines calibrated ML risk scores with versioned deterministic risk rules (`RULE_EXTREME_AMOUNT`, `RULE_HIGH_VELOCITY`, `RULE_NIGHT_HIGH_VALUE`, `RULE_ANOMALOUS_PATTERN`, `RULE_SCORE_BREACH`).
- **SHAP Signal Explainability**: Formulates signal contribution statements explaining model predictions without making false causal claims.
- **Cost-Sensitive Threshold Simulator**: Interactively simulates trade-offs between false-positive friction costs, missed-fraud penalties, and manual review operational expenses.
- **Analyst Investigation Queue**: Full case management interface allowing fraud analysts to inspect evidence and log decision overrides with audit logs.
- **Model Health & Drift Monitoring**: Tracks Population Stability Index (PSI) and feature score shifts.

---

## 5. API Overview

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/v1/health` | GET | Health check & active model version |
| `/api/v1/transactions/score` | POST | Real-time single transaction risk evaluation |
| `/api/v1/transactions/batch-score` | POST | Batch transaction scoring |
| `/api/v1/transactions/{id}` | GET | Fetch transaction details & decision history |
| `/api/v1/cases` | GET | List analyst investigation queue |
| `/api/v1/cases/{id}` | GET | Fetch investigation case details |
| `/api/v1/cases/{id}/override` | POST | Submit analyst decision override with audit justification |
| `/api/v1/simulate/threshold` | POST | Run cost-sensitive threshold what-if simulation |
| `/api/v1/monitoring` | GET | Fetch Population Stability Index (PSI) drift & health |
| `/api/v1/metrics` | GET | Fetch model evaluation metrics |
| `/api/v1/dataset/ingest` | POST | Trigger dataset validation report |
| `/api/v1/model/train` | POST | Trigger model retraining pipeline |

---

## 6. Quick Start & Setup

### Prerequisites
- Python 3.13+
- Node.js v18+ & npm

### Local Installation

```bash
# 1. Clone repository
git clone https://github.com/kg3478/SentinelRisk.git
cd SentinelRisk

# 2. Set up Python virtual environment & dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 3. Download & verify dataset
python data/download_dataset.py

# 4. Run automated test suite
PYTHONPATH=. pytest backend/tests -v

# 5. Start Backend API Server
uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal:

```bash
# 6. Start Next.js Frontend App
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 7. Project Structure

```
sentinelrisk/
├── frontend/                  # Next.js 14 App Router + Tailwind CSS
│   ├── app/                   # Dashboard, Simulator, Cases, Thresholds, Monitoring
│   ├── components/            # Navbar, Sidebar, RiskGauge, DecisionBadge
│   ├── lib/                   # API client
│   └── package.json
│
├── backend/                   # FastAPI Backend Engine
│   ├── app/
│   │   ├── main.py            # FastAPI App & CORS
│   │   ├── api.py             # REST API routers
│   │   ├── config.py          # Configuration settings
│   │   ├── db.py              # SQLAlchemy engine
│   │   ├── models.py          # Database ORM schema (16 tables)
│   │   ├── schemas.py         # Pydantic v2 validation models
│   │   ├── ingestion.py       # Data loading & quality validation
│   │   ├── features.py        # Temporal leakage-safe feature engineering
│   │   ├── rules.py           # Deterministic Risk Rules engine
│   │   ├── model.py           # LightGBM training, calibration & metrics
│   │   ├── scoring.py         # Risk score & level mapping
│   │   ├── explainability.py  # SHAP & signal attribution
│   │   ├── decisions.py       # Decision Policy Engine
│   │   ├── cases.py           # Investigation queue & Analyst overrides
│   │   ├── simulator.py       # Cost-sensitive threshold simulator
│   │   ├── monitoring.py      # Feature drift (PSI) & health
│   │   └── auth.py            # RBAC & JWT auth
│   └── tests/                 # Unit & integration test suite
│
├── data/                      # Dataset ingestion script & provenance docs
├── docs/                      # ARCHITECTURE, PRODUCT, DATA, ML, EVALUATION, LIMITATIONS
├── docker-compose.yml         # Container orchestration
├── render.yaml                # Render Blueprint deployment configuration
├── pytest.ini                 # Pytest configuration
└── README.md
```

---

## 8. Limitations & Planned Engineering Upgrades

The table below outlines current architectural boundaries and the target engineering upgrades designed to overcome them:

| # | Current System Limitation | Technical Constraint | Planned Future Upgrade | Target Engineering Solution |
|---|:---|:---|:---|:---|
| 1 | **Anonymized Research Features** | Dataset features `V1`–`V28` are PCA vectors, omitting raw IP geolocation, device fingerprints, and merchant category codes. | **Graph Neural Networks (GNNs) & Entity Resolution** | Build heterogeneous transaction graphs (`Card` → `IP` → `Device` → `Merchant`) with **PyTorch Geometric / DGL** to detect coordinated fraud rings. |
| 2 | **Batch Historical Data Pipeline** | Ingested from static CSV files rather than streaming authorization events. | **Streaming Event-Driven Architecture** | Deploy **Apache Kafka / Redpanda** + **Apache Flink** for streaming ingestion (>10,000 tx/sec) and stateful sub-second rolling velocity windows. |
| 3 | **Delayed Fraud Chargeback Labels** | Real-world fraud labels arrive with a 30–90 day chargeback lag, complicating real-time supervised updates. | **Adaptive Online ML & Semi-Supervised Learning** | Implement incremental online learning algorithms (**River / Hoeffding Trees**) with semi-supervised pseudo-labeling for unconfirmed transactions. |
| 4 | **Offline Drift Monitoring** | Population Stability Index (PSI) is calculated against fixed historical training partitions. | **Low-Latency Feature Store & Live Drift Alerts** | Integrate **Feast Online Feature Store** + **Evidently AI** to monitor streaming feature drift, concept drift, and data quality in sliding real-time windows. |
| 5 | **Manual Analyst Case Summaries** | Fraud analysts must manually read evidence and rule triggers when investigating flagged cases. | **LLM RAG Analyst Investigation Assistant** | Implement an **LLM Agent** (RAG over transaction features, rule evidence, and SHAP vectors) to automatically generate case investigation summaries. |
| 6 | **Monolithic Auth & Storage** | Embedded SQLite / single DB instance without enterprise multi-tenant access control. | **Enterprise OIDC & Multi-Tenant Isolation** | Integrate **OAuth2 / Keycloak** with fine-grained Role-Based Access Control (RBAC), multi-tenant organization boundaries, and SOC2-compliant audit logs. |

---

## 9. License & Disclaimers

Built under the **MIT License**. Developed for research, interview demonstration, and fintech portfolio evaluation.
