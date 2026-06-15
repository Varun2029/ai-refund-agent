"""Pydantic schemas for customer endpoints."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    tier: str
    total_orders: int
    total_spent: float
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerDetail(CustomerResponse):
    orders: list["OrderResponse"] = []
    refund_requests: list["RefundBrief"] = []


class OrderResponse(BaseModel):
    id: int
    order_number: str
    amount: float
    status: str
    items: Optional[list] = None
    order_date: datetime
    delivered_date: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RefundBrief(BaseModel):
    id: int
    request_id: str
    reason: str
    refund_amount: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
