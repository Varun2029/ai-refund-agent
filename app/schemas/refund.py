"""Pydantic schemas for refund request endpoints."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RefundCreate(BaseModel):
    order_id: int
    reason: str
    refund_amount: Optional[float] = None  # if None, defaults to full order amount


class RefundResponse(BaseModel):
    id: int
    request_id: str
    order_id: int
    customer_id: int
    reason: str
    refund_amount: float
    status: str
    fraud_score: Optional[float] = None
    policy_check: Optional[str] = None
    decision_rationale: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RefundDetail(RefundResponse):
    agent_logs: list["AgentLogResponse"] = []
    order: Optional["OrderBrief"] = None
    customer: Optional["CustomerBrief"] = None


class AgentLogResponse(BaseModel):
    id: int
    agent_name: str
    action: str
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = None
    duration_ms: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderBrief(BaseModel):
    id: int
    order_number: str
    amount: float
    status: str

    model_config = {"from_attributes": True}


class CustomerBrief(BaseModel):
    id: int
    name: str
    email: str
    tier: str

    model_config = {"from_attributes": True}


class ChatMessage(BaseModel):
    """Inbound chat message from the customer UI."""
    message: str
    customer_id: Optional[int] = None
    order_number: Optional[str] = None
