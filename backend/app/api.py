import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.db import get_db, Base, engine
from backend.app.models import Transaction, TransactionFeature, Prediction, RiskScore, TriggeredRule, Decision, Case, CaseNote, AuditLog, Dataset, IngestionRun
from backend.app.schemas import (
    TransactionCreate, TransactionScoreResponse, BatchScoreRequest, BatchScoreResponse,
    CaseResponse, CaseOverrideRequest, CaseNoteCreate, ThresholdSimulationRequest, ThresholdSimulationResponse,
    MonitoringMetricsResponse, ModelVersionResponse, AuditLogResponse, UserResponse
)
from backend.app.features import extract_single_tx_features
from backend.app.model import global_risk_engine
from backend.app.scoring import probability_to_risk_score
from backend.app.rules import evaluate_deterministic_rules
from backend.app.decisions import evaluate_decision_policy
from backend.app.explainability import compute_feature_contributions
from backend.app.simulator import run_threshold_simulation
from backend.app.monitoring import get_system_monitoring_metrics
from backend.app.ingestion import load_and_validate_dataset
from backend.app.auth import get_current_user

# Auto-create database tables
Base.metadata.create_all(bind=engine)

router = APIRouter()

# --- Health Check ---
@router.get("/health", tags=["System"])
def health_check():
    model_loaded = global_risk_engine.load_model()
    return {
        "status": "HEALTHY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_version": global_risk_engine.version,
        "model_loaded": model_loaded,
        "environment": "production-ready"
    }

# --- Transaction Scoring API ---
@router.post("/transactions/score", response_model=TransactionScoreResponse, tags=["Scoring"])
def score_single_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db)):
    """
    Evaluates real-time transaction:
    Feature Generation -> ML Calibrated Risk -> Deterministic Rules -> Hybrid Decision Policy -> Explainability Signals -> Case Creation -> Audit Log
    """
    ext_id = f"TX-{uuid.uuid4().hex[:10].upper()}"
    features = extract_single_tx_features(tx_in.amount, tx_in.time, tx_in.pca_features)

    # 1. ML Calibrated Probability
    if not global_risk_engine.calibrator:
        global_risk_engine.load_model()
    
    calibrated_prob = global_risk_engine.predict_prob(features)
    
    # 2. Risk Score & Level
    risk_score, risk_level = probability_to_risk_score(calibrated_prob)

    # 3. Deterministic Rules
    triggered_rules_raw = evaluate_deterministic_rules(tx_in.amount, tx_in.time, risk_score, features)

    # 4. Decision Policy
    decision, confidence, reasons = evaluate_decision_policy(risk_score, risk_level, triggered_rules_raw)

    # 5. Explainability
    top_signals = compute_feature_contributions(features)

    # 6. Save Transaction Record to Database
    db_tx = Transaction(
        external_tx_id=ext_id,
        time=tx_in.time,
        amount=tx_in.amount,
        is_synthetic=tx_in.is_synthetic,
        ground_truth_label=tx_in.ground_truth_label
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)

    # Save features & decision
    db_feat = TransactionFeature(
        transaction_id=db_tx.id,
        pca_features={k: v for k, v in features.items() if k.startswith("V")},
        amount_log=features["amount_log"],
        amount_zscore=features["amount_zscore"],
        hour_of_day=features["hour_of_day"],
        tx_velocity_1h=features["tx_velocity_1h"]
    )
    db.add(db_feat)

    db_dec = Decision(
        transaction_id=db_tx.id,
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        confidence=confidence,
        reasons_json=reasons
    )
    db.add(db_dec)

    # 7. Automatic Case Creation if REVIEW or BLOCK
    case_created = False
    case_id = None
    if decision in ["REVIEW", "BLOCK"]:
        case_num = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        new_case = Case(
            case_number=case_num,
            transaction_id=db_tx.id,
            status="NEW",
            original_decision=decision,
            priority="CRITICAL" if risk_score >= 75.0 else "HIGH"
        )
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
        case_created = True
        case_id = new_case.id

    db.commit()

    return TransactionScoreResponse(
        transaction_id=db_tx.id,
        external_tx_id=ext_id,
        amount=tx_in.amount,
        timestamp=db_tx.timestamp,
        risk_score=risk_score,
        risk_level=risk_level,
        calibrated_probability=round(calibrated_prob, 4),
        model_version=global_risk_engine.version,
        decision=decision,
        confidence=confidence,
        triggered_rules=triggered_rules_raw,
        top_signals=top_signals,
        reasons=reasons,
        case_created=case_created,
        case_id=case_id
    )

@router.post("/transactions/batch-score", response_model=BatchScoreResponse, tags=["Scoring"])
def score_batch_transactions(batch_in: BatchScoreRequest, db: Session = Depends(get_db)):
    results = []
    for tx in batch_in.transactions:
        res = score_single_transaction(tx, db)
        results.append(res)
    return BatchScoreResponse(total_processed=len(results), scores=results)

@router.get("/transactions/{id}", tags=["Transactions"])
def get_transaction_by_id(id: str, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    dec = db.query(Decision).filter(Decision.transaction_id == id).first()
    return {
        "transaction": tx,
        "decision": dec
    }

# --- Case Management API ---
@router.get("/cases", tags=["Case Management"])
def list_cases(status: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    cases = query.order_by(Case.created_at.desc()).limit(limit).all()
    
    results = []
    for c in cases:
        tx = db.query(Transaction).filter(Transaction.id == c.transaction_id).first()
        dec = db.query(Decision).filter(Decision.transaction_id == c.transaction_id).first()
        results.append({
            "id": c.id,
            "case_number": c.case_number,
            "transaction_id": c.transaction_id,
            "amount": tx.amount if tx else 0.0,
            "risk_score": dec.risk_score if dec else 50.0,
            "original_decision": c.original_decision,
            "status": c.status,
            "override_decision": c.override_decision,
            "override_reason": c.override_reason,
            "priority": c.priority,
            "created_at": c.created_at,
            "updated_at": c.updated_at
        })
    return results

@router.get("/cases/{id}", tags=["Case Management"])
def get_case_detail(id: str, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    tx = db.query(Transaction).filter(Transaction.id == c.transaction_id).first()
    dec = db.query(Decision).filter(Decision.transaction_id == c.transaction_id).first()
    return {
        "case": c,
        "transaction": tx,
        "decision": dec
    }

@router.post("/cases/{id}/override", tags=["Case Management"])
def override_case(id: str, override_req: CaseOverrideRequest, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    
    c.override_decision = override_req.new_decision # APPROVED or REJECTED
    c.override_reason = override_req.reason
    c.status = "APPROVED" if override_req.new_decision == "APPROVED" else "REJECTED"
    c.updated_at = datetime.now(timezone.utc)

    # Log Audit
    audit = AuditLog(
        action="CASE_OVERRIDE",
        entity_type="CASE",
        entity_id=c.id,
        details_json={
            "case_number": c.case_number,
            "new_decision": override_req.new_decision,
            "reason": override_req.reason
        }
    )
    db.add(audit)
    db.commit()
    return {"status": "SUCCESS", "case_id": c.id, "new_status": c.status}

# --- Threshold & Policy Simulation API ---
@router.post("/simulate/threshold", response_model=ThresholdSimulationResponse, tags=["Simulator"])
def simulate_thresholds(req: ThresholdSimulationRequest):
    res = run_threshold_simulation(
        threshold_allow=req.threshold_allow,
        threshold_review=req.threshold_review,
        cost_false_positive=req.cost_false_positive,
        cost_missed_fraud=req.cost_missed_fraud,
        cost_manual_review=req.cost_manual_review
    )
    return ThresholdSimulationResponse(**res)

# --- Monitoring & Metrics API ---
@router.get("/monitoring", response_model=MonitoringMetricsResponse, tags=["Monitoring"])
def get_monitoring_dashboard():
    return MonitoringMetricsResponse(**get_system_monitoring_metrics())

@router.get("/metrics", tags=["Monitoring"])
def get_model_evaluation_metrics():
    if not global_risk_engine.calibrator:
        global_risk_engine.load_model()
    return {
        "version": global_risk_engine.version,
        "metrics": global_risk_engine.metrics
    }

# --- Dataset & Model Management API ---
@router.post("/dataset/ingest", tags=["Dataset"])
def ingest_dataset():
    df, report = load_and_validate_dataset()
    return report

@router.post("/model/train", tags=["Model"])
def retrain_model(bg_tasks: BackgroundTasks):
    df, _ = load_and_validate_dataset()
    metrics = global_risk_engine.train_pipeline(df)
    return {
        "status": "SUCCESS",
        "version": global_risk_engine.version,
        "metrics": metrics
    }
