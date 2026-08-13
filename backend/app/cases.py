import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.models import Case, CaseNote, CaseAuditLog, Transaction, Decision
from backend.app.schemas import CaseResponse, CaseNoteResponse

def create_case_for_transaction(db: Session, transaction_id: str, original_decision: str, risk_score: float) -> Case:
    """Creates a new fraud investigation case for transactions flagged for REVIEW or BLOCK."""
    case_num = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    priority = "CRITICAL" if risk_score >= 75.0 else ("HIGH" if risk_score >= 50.0 else "MEDIUM")

    case = Case(
        case_number=case_num,
        transaction_id=transaction_id,
        status="NEW",
        original_decision=original_decision,
        priority=priority
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

def override_case_decision(
    db: Session, 
    case_id: str, 
    new_decision: str, 
    reason: str, 
    user_id: Optional[str] = "ANALYST_01"
) -> Case:
    """Analyst overrides system decision on a flagged case. Logs full audit record."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    old_status = case.status
    case.override_decision = new_decision # "APPROVED" (ALLOW) or "REJECTED" (BLOCK)
    case.override_reason = reason
    case.status = "APPROVED" if new_decision == "APPROVED" else "REJECTED"
    case.updated_at = datetime.now(timezone.utc)

    # Record Audit Log
    audit = CaseAuditLog(
        user_id=user_id,
        action="OVERRIDE_DECISION",
        entity_type="CASE",
        entity_id=case.id,
        details_json={
            "case_number": case.case_number,
            "original_decision": case.original_decision,
            "new_decision": new_decision,
            "reason": reason,
            "previous_status": old_status,
            "new_status": case.status
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(case)
    return case
