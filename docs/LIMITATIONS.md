# SentinelRisk — Technical Limitations & Future Engineering Roadmap

## Overview

SentinelRisk is engineered as a production-grade transaction risk scoring and fraud decision intelligence platform. This document explicitly documents current system boundaries alongside the target architectural upgrades designed to address them.

---

## Technical Mapping: Limitations vs. Future Engineering Solutions

| # | Current System Limitation | Technical Constraint | Planned Future Upgrade | Target Engineering Solution |
|---|:---|:---|:---|:---|
| 1 | **Anonymized Research Features** | Dataset features `V1`–`V28` are PCA vectors, omitting raw IP geolocation, device fingerprints, and merchant category codes. | **Graph Neural Networks (GNNs) & Entity Resolution** | Build heterogeneous transaction graphs (`Card` → `IP` → `Device` → `Merchant`) with **PyTorch Geometric / DGL** to detect coordinated fraud rings. |
| 2 | **Batch Historical Data Pipeline** | Ingested from static CSV files rather than streaming authorization events. | **Streaming Event-Driven Architecture** | Deploy **Apache Kafka / Redpanda** + **Apache Flink** for streaming ingestion (>10,000 tx/sec) and stateful sub-second rolling velocity windows. |
| 3 | **Delayed Fraud Chargeback Labels** | Real-world fraud labels arrive with a 30–90 day chargeback lag, complicating real-time supervised updates. | **Adaptive Online ML & Semi-Supervised Learning** | Implement incremental online learning algorithms (**River / Hoeffding Trees**) with semi-supervised pseudo-labeling for unconfirmed transactions. |
| 4 | **Offline Drift Monitoring** | Population Stability Index (PSI) is calculated against fixed historical training partitions. | **Low-Latency Feature Store & Live Drift Alerts** | Integrate **Feast Online Feature Store** + **Evidently AI** to monitor streaming feature drift, concept drift, and data quality in sliding real-time windows. |
| 5 | **Manual Analyst Case Summaries** | Fraud analysts must manually read evidence and rule triggers when investigating flagged cases. | **LLM RAG Analyst Investigation Assistant** | Implement an **LLM Agent** (RAG over transaction features, rule evidence, and SHAP vectors) to automatically generate case investigation summaries. |
| 6 | **Monolithic Auth & Storage** | Embedded SQLite / single DB instance without enterprise multi-tenant access control. | **Enterprise OIDC & Multi-Tenant Isolation** | Integrate **OAuth2 / Keycloak** with fine-grained Role-Based Access Control (RBAC), multi-tenant organization boundaries, and SOC2-compliant audit logs. |

---

## Research Data Disclaimer

SentinelRisk utilizes the MLG-ULB Credit Card Fraud Detection benchmark dataset (284,807 European card transactions). The dataset is used for model development, Platt scaling calibration, threshold optimization, and reproducible evaluation. It does not represent live streaming production data from any card network or financial institution.
