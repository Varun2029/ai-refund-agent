"""
Escalation API routes — list, resolve, and manage escalations.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Escalation, RefundRequest, Customer, Order, User
from app.schemas.analytics import EscalationResponse, EscalationResolve
from app.api.auth import get_current_user

router = APIRouter()


@router.get("", response_model=list[EscalationResponse])
def list_escalations(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all escalations, optionally filtered by status."""
    query = (
        db.query(
            Escalation,
            RefundRequest.request_id,
            Customer.name.label("customer_name"),
            Order.order_number,
            User.full_name.label("assigned_name"),
        )
        .join(RefundRequest, Escalation.refund_request_id == RefundRequest.id)
        .outerjoin(Customer, RefundRequest.customer_id == Customer.id)
        .outerjoin(Order, RefundRequest.order_id == Order.id)
        .outerjoin(User, Escalation.assigned_to == User.id)
    )
    if status_filter:
        query = query.filter(Escalation.status == status_filter)

    query = query.order_by(Escalation.created_at.desc())
    rows = query.all()

    result = []
    for esc, request_id, customer_name, order_number, assigned_name in rows:
        result.append(
            EscalationResponse(
                id=esc.id,
                refund_request_id=esc.refund_request_id,
                request_id=request_id,
                customer_name=customer_name or "Unknown",
                order_number=order_number or "N/A",
                reason=esc.reason,
                priority=esc.priority,
                status=esc.status,
                assigned_to_name=assigned_name,
                resolution_notes=esc.resolution_notes,
                created_at=esc.created_at,
                resolved_at=esc.resolved_at,
            )
        )

    return result


@router.post("/{escalation_id}/resolve", response_model=EscalationResponse)
def resolve_escalation(
    escalation_id: int,
    body: EscalationResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resolve an escalation — approve or deny the refund."""
    esc = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not esc:
        raise HTTPException(status_code=404, detail="Escalation not found")

    if esc.status == "resolved":
        raise HTTPException(status_code=400, detail="Escalation already resolved")

    # Update escalation
    esc.status = "resolved"
    esc.resolution_notes = body.resolution_notes
    esc.assigned_to = current_user.id
    esc.resolved_at = datetime.now(timezone.utc)

    # Update the refund request
    refund = db.query(RefundRequest).filter(RefundRequest.id == esc.refund_request_id).first()
    if refund:
        refund.status = body.decision  # "approved" or "denied"
        refund.decision_rationale = f"Manager resolution: {body.resolution_notes}"
        refund.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(esc)

    # Fetch joined data for response
    refund = db.query(RefundRequest).filter(RefundRequest.id == esc.refund_request_id).first()
    customer = db.query(Customer).filter(Customer.id == refund.customer_id).first()
    order = db.query(Order).filter(Order.id == refund.order_id).first()

    return EscalationResponse(
        id=esc.id,
        refund_request_id=esc.refund_request_id,
        request_id=refund.request_id if refund else "",
        customer_name=customer.name if customer else "Unknown",
        order_number=order.order_number if order else "N/A",
        reason=esc.reason,
        priority=esc.priority,
        status=esc.status,
        assigned_to_name=current_user.full_name,
        resolution_notes=esc.resolution_notes,
        created_at=esc.created_at,
        resolved_at=esc.resolved_at,
    )
