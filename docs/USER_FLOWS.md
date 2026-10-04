# SentinelRisk — User Flows & Operational Journeys

## 1. Overview & Stakeholder Personas

SentinelRisk coordinates multiple operational personas across the lifecycle of a financial transaction. Rather than serving as an isolated algorithmic classifier, the system orchestrates real-time automated decisions with human-in-the-loop oversight and business policy simulation.

```mermaid
mindmap
  root((SentinelRisk Users))
    Payment Client / Consumer
      Real-Time Authorization
      3DS Step-Up Verification
      Instant Clearance
    Fraud Analyst
      Investigation Queue
      Evidence Inspection
      Decision Override
      Case Notes & Audits
    Risk Manager
      Threshold Simulator
      False Positive Economics
      Policy Deployment
      Executive KPI Tracking
    ML / Platform Engineer
      Drift Monitoring PSI
      Latency SLA Guardrails
      Retraining Pipelines
      Data Quality Audits
```

---

## 2. Global Operational Flow Diagram

![SentinelRisk User Flow Diagram](assets/user_flow_diagram.svg)

---

## 3. Journey 1: Real-Time Payment Authorization Lifecycle

The primary transactional flow executes within a strict sub-20ms latency window when a cardholder attempts an online purchase.

```mermaid
flowchart TD
    Start([Cardholder Submits Payment]) --> Ingress[Payment Gateway sends POST /transactions/score]
    Ingress --> Feat[Feature Store extracts rolling velocities & transforms]
    Feat --> Scoring{Dual Risk Assessment}
    
    Scoring -->|ML Pipeline| ML[Calibrated LightGBM predicts Risk Score 0-100]
    Scoring -->|Rule Engine| Rules[Deterministic Safety Rules evaluated]

    ML --> Policy[Decision Policy Arbiter]
    Rules --> Policy

    Policy --> Route{Decision Action}

    Route -->|Score <= 20 & No Rules| Allow[Action: ALLOW]
    Route -->|20 < Score <= 50 OR Med Rule| Challenge[Action: CHALLENGE]
    Route -->|50 < Score < 75 OR High Rule| Review[Action: REVIEW]
    Route -->|Score >= 75 OR Critical Rule| Block[Action: BLOCK]

    Allow --> Clear[Transaction Approved - Cleared in &lt;15ms]
    Challenge --> StepUp[Prompt Customer for 3DS / SMS OTP]
    StepUp -->|Success| Clear
    StepUp -->|Failed / Timeout| Block

    Review --> Hold[Transaction Held / Flagged for Analyst]
    Review --> CreateCase1[Dispatch Case to Analyst Queue]

    Block --> Decline[Transaction Declined to Merchant]
    Block --> CreateCase2[Dispatch Case to High Priority Queue]

    Clear --> Audit[Persist Transaction & Log Immutable Audit Trail]
    Decline --> Audit
```

### Detailed Operational Steps:
1. **Ingress**: Payment gateway submits authorization payload containing `amount`, `time`, and contextual features to `POST /api/v1/transactions/score`.
2. **Feature Extraction**: Instantaneous features ($Z$-scores, log amount, cyclical hour of day) and rolling velocity metrics are computed ($t \le T$).
3. **Dual Assessment**:
   - **Machine Learning**: Generates a calibrated risk score between `0.0` and `100.0`.
   - **Rule Engine**: Concurrently executes 5 deterministic safety rules to flag immediate operational violations.
4. **Policy Arbitration**: Synthesizes the score and rule severities into one of four action outcomes:
   - **`ALLOW`**: Low risk; approved without customer friction.
   - **`CHALLENGE`**: Moderate risk; prompts cardholder for step-up verification.
   - **`REVIEW`**: Elevated risk; routed to fraud analysts for inspection.
   - **`BLOCK`**: High risk; declined immediately to prevent chargebacks.
5. **Audit Persistence**: Every decision, rule evidence payload, and SHAP signal vector is written to the database.

---

## 4. Journey 2: Fraud Analyst Investigation & Decision Override

Fraud analysts investigate transactions routed to the manual review queue or critical blocked cases.

```mermaid
sequenceDiagram
    autonumber
    actor Analyst as Fraud Analyst
    participant UI as Analyst Queue (/cases)
    participant API as FastAPI Backend (/cases)
    participant DB as Cases & Audit Schema
    actor Customer as Cardholder

    Analyst->>UI: Opens Investigation Queue (/cases)
    UI->>API: GET /api/v1/cases?status=NEW
    API->>DB: Query pending cases ordered by priority (CRITICAL, HIGH)
    DB-->>API: Return case list with risk scores & amounts
    API-->>UI: Render case table

    Analyst->>UI: Selects case (e.g. CASE-9F2B81)
    UI->>API: GET /api/v1/cases/{id}
    API-->>UI: Return full transaction evidence, triggered rules & SHAP signals

    Note over Analyst,UI: Analyst inspects evidence:<br/>- Rule: RULE_EXTREME_AMOUNT (€3,800)<br/>- SHAP Signal: V14 deviation (-5.2)<br/>- 1-hour velocity: 4 transactions

    opt Outreach Verification
        Analyst->>Customer: Phone / SMS security verification
        Customer-->>Analyst: Confirms authorized luxury purchase
    end

    Analyst->>UI: Selects Override: "APPROVED"
    Analyst->>UI: Enters Mandatory Audit Reason: "Cardholder confirmed luxury purchase via phone verification."
    UI->>API: POST /api/v1/cases/{id}/override
    API->>DB: Update Case status = APPROVED
    API->>DB: Insert record into audit_logs (Actor ID, Action, Timestamp, Diff)
    DB-->>API: Commit transaction
    API-->>UI: Success confirmation & update queue
```

### Analyst Workflow States:
- **Case Ingestion**: Automatic creation when decision is `REVIEW` or `BLOCK`.
- **Evidence Review**: Analyst inspects:
  1. Calibrated Risk Score (e.g., `78.4 / 100`).
  2. Triggered Rule Evidence (exact values vs thresholds).
  3. Top SHAP signal attributions explaining feature weights.
  4. Temporal velocity history.
- **Decision Override**: The analyst may override the automated verdict:
  - `APPROVED`: False positive released.
  - `REJECTED`: Confirmed fraudulent attempt; card frozen.
- **Mandatory Audit Logging**: Overrides require justification text; written to append-only audit tables for regulatory compliance.

---

## 5. Journey 3: Risk Manager Policy Tuning & Threshold Simulation

Risk managers configure decision boundaries to balance fraud losses against customer friction and operational review costs.

```mermaid
flowchart TD
    RM[Risk Manager opens /thresholds] --> Dash[Review Current Portfolio Performance]
    Dash -->|PR-AUC: 0.8542, FPR: 0.84%| SimControls[Configure What-If Simulation Sliders]

    subgraph Simulation Parameters
        T1[Allow Cutoff: 0 - 50]
        T2[Review Cutoff: 50 - 90]
        C1[Cost per False Positive: $50]
        C2[Cost per Missed Fraud: $100 + Chargeback]
        C3[Cost per Manual Review: $15]
    end

    SimControls --> T1 & T2 & C1 & C2 & C3
    T1 & T2 & C1 & C2 & C3 --> Run[Execute POST /simulate/threshold]

    Run --> Engine[Simulation Engine evaluates 42,722 test transactions]
    Engine --> Calc[Compute Financial Impact & Trade-Offs]

    Calc --> Out1[Fraud Capture Rate %]
    Calc --> Out2[False Positive Rate %]
    Calc --> Out3[Total Financial Impact $]

    Out1 & Out2 & Out3 --> Comp{Evaluate Net Business Impact}
    Comp -->|Excessive FP Friction| RaiseAllow[Raise Allow Threshold to reduce challenges]
    Comp -->|Elevated Fraud Losses| LowerReview[Lower Review Threshold to catch fraud]
    Comp -->|Optimal Operating Point| Deploy[Deploy Policy Configuration to Production]
```

### Optimization Dynamics:
- **Cost Minimization**: The platform solves for the optimal threshold tuple $(\theta_{\text{allow}}^*, \theta_{\text{review}}^*)$ that minimizes:
  $$\text{Total Cost} = \text{Loss}_{\text{missed fraud}} + \text{Cost}_{\text{FP friction}} + \text{Cost}_{\text{manual review}}$$
- **Live Sandbox**: The Next.js frontend recalculates outcomes in real time across the unseen test split.

---

## 6. Journey 4: Platform & MLOps Engineer Governance & Retraining

ML engineers monitor model health, feature drift, and trigger continuous retraining.

```mermaid
sequenceDiagram
    autonumber
    actor MLE as ML / Platform Engineer
    participant MonUI as Monitoring Console (/monitoring)
    participant API as FastAPI Monitoring Router
    participant Engine as Drift & Risk Engine
    participant Pipeline as Model Retraining Pipeline

    MLE->>MonUI: Accesses /monitoring
    MonUI->>API: GET /api/v1/monitoring
    API->>Engine: calculate_population_stability_index()
    Engine-->>API: Return PSI (0.0182), Latency (14.5ms), Metrics
    API-->>MonUI: Render Monitoring Dashboards & Health Status

    alt PSI < 0.10 (Stable)
        MonUI-->>MLE: Status: HEALTHY (Zero concept drift detected)
    else PSI >= 0.10 (Drift Detected)
        MonUI-->>MLE: Status: WARNING (Distribution shift detected)
        MLE->>MonUI: Clicks "Trigger Automated Retrain"
        MonUI->>API: POST /api/v1/model/train
        API->>Pipeline: train_pipeline(df)
        Pipeline->>Pipeline: Compute temporal features & split chronologically
        Pipeline->>Pipeline: Fit LightGBM + Platt Scaling Calibrator
        Pipeline->>Pipeline: Evaluate PR-AUC, ROC-AUC, Brier score
        Pipeline-->>API: New model version artifact saved
        API-->>MonUI: Retraining Complete (Updated PR-AUC: 0.8542)
    end
```

---

## 7. State Machine Specifications

### 7.1 Transaction State Machine

```mermaid
stateDiagram-v2
    [*] --> RECEIVED : POST /transactions/score
    RECEIVED --> EVALUATING : Extract Features
    EVALUATING --> SCORED : ML Model & Rules Completed
    
    SCORED --> ALLOWED : Risk Score <= 20 & No Rules
    SCORED --> CHALLENGED : 20 < Score <= 50 OR Med Rule
    SCORED --> REVIEW_QUEUED : 50 < Score < 75 OR High Rule
    SCORED --> BLOCKED : Score >= 75 OR Critical Rule

    CHALLENGED --> ALLOWED : Step-Up 2FA Verified
    CHALLENGED --> BLOCKED : 2FA Failed / Expired

    REVIEW_QUEUED --> OVERRIDDEN_APPROVED : Analyst Approved
    REVIEW_QUEUED --> OVERRIDDEN_REJECTED : Analyst Rejected

    BLOCKED --> OVERRIDDEN_APPROVED : False Positive Override

    ALLOWED --> SETTLED : Payment Captured
    BLOCKED --> SETTLED : Transaction Aborted
    OVERRIDDEN_APPROVED --> SETTLED : Payment Released
    OVERRIDDEN_REJECTED --> SETTLED : Hard Reject Confirmed

    SETTLED --> [*]
```

### 7.2 Investigation Case State Machine

```mermaid
stateDiagram-v2
    [*] --> NEW : Auto-created from REVIEW or BLOCK
    NEW --> INVESTIGATING : Analyst opens case
    INVESTIGATING --> ESCALATED : Requires Senior Review
    ESCALATED --> INVESTIGATING : Returned with guidance
    INVESTIGATING --> APPROVED : Override to ALLOW (with reason)
    INVESTIGATING --> REJECTED : Confirm Fraud BLOCK (with reason)
    APPROVED --> CLOSED : Audit log recorded
    REJECTED --> CLOSED : Card block & alert logged
    CLOSED --> [*]
```
