from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- User & Auth Schemas ---
class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "FRAUD_ANALYST"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Transaction & Scoring Schemas ---
class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount in EUR / Currency unit")
    time: float = Field(..., ge=0, description="Time delta or timestamp in seconds")
    pca_features: Optional[Dict[str, float]] = Field(default=None, description="PCA vectors V1-V28 (generated if omitted)")
    is_synthetic: bool = False
    ground_truth_label: Optional[int] = None

class FeatureSignal(BaseModel):
    feature_name: str
    contribution: float
    direction: str # "POS_RISK" (increases risk) or "NEG_RISK" (decreases risk)
    description: str

class TriggeredRuleSchema(BaseModel):
    rule_id: str
    rule_name: str
    severity: str
    evidence: Dict[str, Any]
    explanation: str

class TransactionScoreResponse(BaseModel):
    transaction_id: str
    external_tx_id: str
    amount: float
    timestamp: datetime
    risk_score: float # 0.0 - 100.0
    risk_level: str   # LOW, MEDIUM, HIGH, CRITICAL
    calibrated_probability: float
    model_version: str
    decision: str     # ALLOW, CHALLENGE, REVIEW, BLOCK
    confidence: float
    triggered_rules: List[TriggeredRuleSchema]
    top_signals: List[FeatureSignal]
    reasons: List[str]
    case_created: bool
    case_id: Optional[str] = None

class BatchScoreRequest(BaseModel):
    transactions: List[TransactionCreate]

class BatchScoreResponse(BaseModel):
    total_processed: int
    scores: List[TransactionScoreResponse]

# --- Case & Investigation Schemas ---
class CaseNoteCreate(BaseModel):
    note_text: str

class CaseNoteResponse(BaseModel):
    id: str
    author_id: str
    author_name: Optional[str] = "Analyst"
    note_text: str
    created_at: datetime

    class Config:
        from_attributes = True

class CaseOverrideRequest(BaseModel):
    new_decision: str # APPROVED (overrides to ALLOW), REJECTED (overrides to BLOCK)
    reason: str

class CaseResponse(BaseModel):
    id: str
    case_number: str
    transaction_id: str
    amount: float
    risk_score: float
    original_decision: str
    status: str # NEW, INVESTIGATING, ESCALATED, APPROVED, REJECTED, CLOSED
    assigned_analyst: Optional[str] = None
    override_decision: Optional[str] = None
    override_reason: Optional[str] = None
    priority: str
    created_at: datetime
    updated_at: datetime
    notes: List[CaseNoteResponse] = []

    class Config:
        from_attributes = True

# --- Threshold & Simulation Schemas ---
class ThresholdSimulationRequest(BaseModel):
    threshold_allow: float = 20.0     # Risk score cutoff for ALLOW
    threshold_review: float = 75.0    # Risk score cutoff for REVIEW vs BLOCK
    cost_false_positive: float = 50.0  # Cost per legit transaction blocked/friction
    cost_missed_fraud: float = 100.0   # Base penalty + chargeback fee on top of fraud value
    cost_manual_review: float = 15.0   # Analyst operational cost per case

class ThresholdSimulationResponse(BaseModel):
    threshold_allow: float
    threshold_review: float
    total_transactions: int
    total_fraud_count: int
    fraud_captured_count: int
    fraud_capture_rate: float # %
    false_positive_count: int
    false_positive_rate: float # %
    approval_rate: float
    review_rate: float
    block_rate: float
    estimated_fraud_loss: float
    estimated_false_positive_cost: float
    estimated_review_cost: float
    total_financial_impact: float
    recommendation: str

# --- Monitoring & Model Schemas ---
class ModelVersionResponse(BaseModel):
    id: str
    version: str
    model_type: str
    dataset_version: str
    feature_version: str
    metrics: Dict[str, float]
    is_active: bool
    calibrated: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MonitoringMetricsResponse(BaseModel):
    total_scored_transactions: int
    fraud_rate_estimate: float
    avg_risk_score: float
    risk_distribution: Dict[str, int] # LOW, MEDIUM, HIGH, CRITICAL counts
    decision_breakdown: Dict[str, int] # ALLOW, CHALLENGE, REVIEW, BLOCK counts
    active_model_version: str
    model_pr_auc: float
    model_brier_score: float
    system_latency_ms: float

class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    details: Dict[str, Any]
    timestamp: datetime

    class Config:
        from_attributes = True
