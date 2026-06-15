"""
Dashboard API routes — manager stats and review queue.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import RefundRequest, Escalation, Customer, Order, User
from app.schemas.analytics import DashboardStats, QueueItem
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get summary statistics for the manager dashboard."""
    total = db.query(func.count(RefundRequest.id)).scalar() or 0
    pending = db.query(func.count(RefundRequest.id)).filter(RefundRequest.status == "pending").scalar() or 0
    processing = db.query(func.count(RefundRequest.id)).filter(RefundRequest.status == "processing").scalar() or 0
    approved = db.query(func.count(RefundRequest.id)).filter(RefundRequest.status == "approved").scalar() or 0
    denied = db.query(func.count(RefundRequest.id)).filter(RefundRequest.status == "denied").scalar() or 0
    escalated = db.query(func.count(RefundRequest.id)).filter(RefundRequest.status == "escalated").scalar() or 0

    avg_fraud = db.query(func.avg(RefundRequest.fraud_score)).filter(RefundRequest.fraud_score.isnot(None)).scalar() or 0.0
    total_amount = db.query(func.sum(RefundRequest.refund_amount)).filter(RefundRequest.status == "approved").scalar() or 0.0
    open_escalations = db.query(func.count(Escalation.id)).filter(Escalation.status == "open").scalar() or 0

    approval_rate = (approved / total * 100) if total > 0 else 0.0

    return DashboardStats(
        total_refunds=total,
        pending_refunds=pending + processing,
        approved_refunds=approved,
        denied_refunds=denied,
        escalated_refunds=escalated,
        approval_rate=round(approval_rate, 1),
        avg_fraud_score=round(float(avg_fraud), 1),
        total_refund_amount=round(float(total_amount), 2),
        open_escalations=open_escalations,
    )


@router.get("/queue", response_model=list[QueueItem])
def get_review_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the manager review queue — pending and escalated refunds."""
    refunds = (
        db.query(RefundRequest, Customer.name, Order.order_number)
        .join(Customer, RefundRequest.customer_id == Customer.id)
        .join(Order, RefundRequest.order_id == Order.id)
        .filter(RefundRequest.status.in_(["pending", "processing", "escalated"]))
        .order_by(RefundRequest.created_at.desc())
        .all()
    )

    return [
        QueueItem(
            id=r.RefundRequest.id,
            request_id=r.RefundRequest.request_id,
            customer_name=r.name,
            order_number=r.order_number,
            reason=r.RefundRequest.reason,
            refund_amount=r.RefundRequest.refund_amount,
            fraud_score=r.RefundRequest.fraud_score,
            status=r.RefundRequest.status,
            created_at=r.RefundRequest.created_at,
        )
        for r in refunds
    ]
