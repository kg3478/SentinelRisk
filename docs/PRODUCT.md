# SentinelRisk — Product Specifications & Vision

## Product Problem Statement

In digital payments and fintech:
1. Fraud is extremely rare (~0.17%), making raw accuracy misleading.
2. Blocking legitimate users (False Positives) damages customer lifetime value and causes revenue friction.
3. Classifiers output raw probabilities; platforms need actionable decisions (`ALLOW`, `CHALLENGE`, `REVIEW`, `BLOCK`).
4. Regulators and risk managers require clear explainability and full auditability for every declined or reviewed transaction.

SentinelRisk solves these challenges by providing an end-to-end transaction decision intelligence platform.

---

## Target User Personas & Journeys

### 1. Fraud Analyst
- **Goal**: Rapidly investigate suspicious transactions and resolve queued cases.
- **Workflow**: Open Investigation Queue -> Inspect Risk Score, Triggered Rules & SHAP Signals -> Override Decision if false positive -> Log audit reason.

### 2. Risk Manager
- **Goal**: Balance fraud capture against customer friction.
- **Workflow**: Open Decision Simulator -> Tweak risk cutoffs & cost parameters -> Observe net financial savings -> Deploy updated policy.

### 3. Engineering & ML Team
- **Goal**: Monitor model health, feature drift, and scoring latency.
- **Workflow**: Open Model Monitoring -> Inspect Population Stability Index (PSI), PR-AUC metrics, and Brier calibration score.
