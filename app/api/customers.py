"""
Customer API routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.db.models import Customer, User
from app.schemas.customer import CustomerResponse, CustomerDetail
from app.api.auth import get_current_user

router = APIRouter()


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all customers."""
    customers = (
        db.query(Customer)
        .order_by(Customer.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [CustomerResponse.model_validate(c) for c in customers]


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get customer detail with orders and refund history."""
    customer = (
        db.query(Customer)
        .options(
            joinedload(Customer.orders),
            joinedload(Customer.refund_requests),
        )
        .filter(Customer.id == customer_id)
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
