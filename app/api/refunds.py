"""
Refund API routes — CRUD and workflow trigger.
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.db.models import RefundRequest, AgentLog, User
from app.schemas.refund import RefundCreate, RefundResponse, RefundDetail, AgentLogResponse, ChatMessage
from app.api.auth import get_current_user
from app.services.refund_service import process_refund
from app.db.models import Customer

router = APIRouter()


@router.get("", response_model=list[RefundResponse])
def list_refunds(
    status_filter: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all refund requests, optionally filtered by status."""
    query = db.query(RefundRequest).order_by(RefundRequest.created_at.desc())
    if status_filter:
        query = query.filter(RefundRequest.status == status_filter)
    refunds = query.offset(skip).limit(limit).all()
    return [RefundResponse.model_validate(r) for r in refunds]


@router.get("/history", response_model=list[RefundDetail])
def get_customer_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the refund history (including agent logs) for the logged-in customer."""
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    if not customer:
        return []

    refunds = (
        db.query(RefundRequest)
        .options(
            joinedload(RefundRequest.agent_logs),
            joinedload(RefundRequest.order),
            joinedload(RefundRequest.customer),
        )
        .filter(RefundRequest.customer_id == customer.id)
        .order_by(RefundRequest.created_at.asc())
        .all()
    )

    result = []
    for r in refunds:
        order_dict = {"id": r.order.id, "order_number": r.order.order_number, "amount": r.order.amount, "status": r.order.status} if r.order else None
        customer_dict = {"id": r.customer.id, "name": r.customer.name, "email": r.customer.email, "tier": r.customer.tier} if r.customer else None
        
        from app.schemas.refund import AgentLogResponse
        agent_logs = [AgentLogResponse.model_validate(log) for log in r.agent_logs]
        
        detail = RefundDetail(
            id=r.id,
            request_id=r.request_id,
            order_id=r.order_id,
            customer_id=r.customer_id,
            order=order_dict,
            customer=customer_dict,
            reason=r.reason,
            refund_amount=r.refund_amount,
            status=r.status,
            fraud_score=r.fraud_score,
            policy_check=r.policy_check,
            decision_rationale=r.decision_rationale,
            agent_logs=agent_logs,
            created_at=r.created_at,
            resolved_at=r.resolved_at,
        )
        result.append(detail)
        
    return result


@router.get("/{refund_id}", response_model=RefundDetail)
def get_refund(
    refund_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get refund request detail with agent logs."""
    refund = (
        db.query(RefundRequest)
        .options(
            joinedload(RefundRequest.agent_logs),
            joinedload(RefundRequest.order),
            joinedload(RefundRequest.customer),
        )
        .filter(RefundRequest.id == refund_id)
        .first()
    )
    if not refund:
        raise HTTPException(status_code=404, detail="Refund request not found")

    return RefundDetail.model_validate(refund)


@router.post("", response_model=dict)
async def create_refund(
    body: RefundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new refund request and trigger the AI workflow."""
    from app.db.models import Order

    order = db.query(Order).filter(Order.id == body.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    refund_amount = body.refund_amount or order.amount

    result = await process_refund(
        db=db,
        customer_message=body.reason,
        customer_id=order.customer_id,
        order_number=order.order_number,
    )

    return result


@router.get("/{refund_id}/logs", response_model=list[AgentLogResponse])
def get_refund_logs(
    refund_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get agent reasoning logs for a specific refund request."""
    logs = (
        db.query(AgentLog)
        .filter(AgentLog.refund_request_id == refund_id)
        .order_by(AgentLog.created_at)
        .all()
    )
    return [AgentLogResponse.model_validate(log) for log in logs]
