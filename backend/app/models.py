from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.db import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="FRAUD_ANALYST") # ADMIN, FRAUD_ANALYST, RISK_MANAGER, PRODUCT_MANAGER, VIEWER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    row_count = Column(Integer, nullable=False)
    fraud_count = Column(Integer, nullable=False)
    fraud_rate = Column(Float, nullable=False)
    ingested_at = Column(DateTime(timezone=True), default=utc_now)

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    dataset_id = Column(String, ForeignKey("datasets.id"))
    status = Column(String, nullable=False) # SUCCESS, FAILED, WARNING
    report_json = Column(JSON, nullable=True)
    run_timestamp = Column(DateTime(timezone=True), default=utc_now)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    external_tx_id = Column(String, unique=True, index=True)
    time = Column(Float, nullable=False) # Seconds from start
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now)
    is_synthetic = Column(Boolean, default=False)
    ground_truth_label = Column(Integer, nullable=True) # 1 = Fraud, 0 = Legitimate, None = Unlabeled
    
    # Relationships
    features = relationship("TransactionFeature", back_populates="transaction", uselist=False, cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="transaction", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="transaction", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="transaction", cascade="all, delete-orphan")

class TransactionFeature(Base):
    __tablename__ = "transaction_features"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False, unique=True)
    feature_version = Column(String, default="v1.0.0")
    
    # Raw PCA features V1-V28
    pca_features = Column(JSON, nullable=False) # {"V1": 0.12, "V2": -0.4, ...}
    
    # Temporal & Behavioral Aggregated Features
    amount_log = Column(Float, nullable=True)
    amount_zscore = Column(Float, nullable=True)
    amount_pct_rank = Column(Float, nullable=True)
    tx_velocity_1h = Column(Integer, default=1)
    tx_velocity_6h = Column(Integer, default=1)
    tx_velocity_24h = Column(Integer, default=1)
    amount_sum_24h = Column(Float, default=0.0)
    hour_of_day = Column(Integer, default=0)
    day_of_week = Column(Integer, default=0)
    time_delta_prev_tx = Column(Float, default=0.0)
    
    transaction = relationship("Transaction", back_populates="features")

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    version = Column(String, unique=True, nullable=False) # e.g. "v1.0.0-lightgbm"
    model_type = Column(String, nullable=False) # LogisticRegression, LightGBM, XGBoost
    dataset_version = Column(String, nullable=False)
    feature_version = Column(String, nullable=False)
    hyperparameters = Column(JSON, nullable=False)
    metrics = Column(JSON, nullable=False) # {pr_auc, roc_auc, f1, precision, recall, brier_score}
    is_active = Column(Boolean, default=False)
    calibrated = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)
    raw_probability = Column(Float, nullable=False)
    calibrated_probability = Column(Float, nullable=False)
    shap_explanations = Column(JSON, nullable=True) # Top signal contributions
    created_at = Column(DateTime(timezone=True), default=utc_now)

    transaction = relationship("Transaction", back_populates="predictions")

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    score = Column(Float, nullable=False) # 0.0 - 100.0
    risk_level = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime(timezone=True), default=utc_now)

class TriggeredRule(Base):
    __tablename__ = "triggered_rules"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    rule_id = Column(String, nullable=False) # e.g. RULE_HIGH_VELOCITY
    rule_name = Column(String, nullable=False)
    severity = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    evidence_json = Column(JSON, nullable=False)
    explanation = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    decision = Column(String, nullable=False) # ALLOW, CHALLENGE, REVIEW, BLOCK
    policy_version = Column(String, default="p1.0.0")
    confidence = Column(Float, default=0.95)
    reasons_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    transaction = relationship("Transaction", back_populates="decisions")

class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, default=generate_uuid)
    case_number = Column(String, unique=True, nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    assigned_analyst_id = Column(String, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="NEW") # NEW, INVESTIGATING, ESCALATED, APPROVED, REJECTED, CLOSED
    original_decision = Column(String, nullable=False)
    override_decision = Column(String, nullable=True)
    override_reason = Column(Text, nullable=True)
    priority = Column(String, default="HIGH") # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    transaction = relationship("Transaction", back_populates="cases")
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan")

class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    case = relationship("Case", back_populates="notes")

class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)
    eval_split = Column(String, nullable=False) # TRAIN, VALIDATION, TEST
    pr_auc = Column(Float, nullable=False)
    roc_auc = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    brier_score = Column(Float, nullable=False)
    false_positive_rate = Column(Float, nullable=False)
    evaluation_timestamp = Column(DateTime(timezone=True), default=utc_now)

class DriftMetric(Base):
    __tablename__ = "drift_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)
    metric_name = Column(String, nullable=False) # PSI, KS_STAT, SCORE_DRIFT
    feature_name = Column(String, nullable=True)
    drift_score = Column(Float, nullable=False)
    is_drifted = Column(Boolean, default=False)
    measured_at = Column(DateTime(timezone=True), default=utc_now)

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    threshold_allow = Column(Float, nullable=False)
    threshold_review = Column(Float, nullable=False)
    cost_false_positive = Column(Float, nullable=False)
    cost_missed_fraud = Column(Float, nullable=False)
    cost_manual_review = Column(Float, nullable=False)
    results_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=True)
    action = Column(String, nullable=False) # OVERRIDE_DECISION, CASE_STATUS_CHANGE, THRESHOLD_UPDATE
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    details_json = Column(JSON, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now)
