"""Pydantic schemas for analytics and dashboard endpoints."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DashboardStats(BaseModel):
    total_refunds: int
    pending_refunds: int
    approved_refunds: int
    denied_refunds: int
    escalated_refunds: int
    approval_rate: float  # percentage
    avg_fraud_score: float
    total_refund_amount: float
    open_escalations: int


class RefundTimeSeries(BaseModel):
    date: str
    approved: int
    denied: int
    escalated: int
    pending: int


class FraudDistribution(BaseModel):
    range_label: str  # e.g. "0-10", "10-20", etc.
    count: int


class AgentPerformanceMetric(BaseModel):
    agent_name: str
    avg_duration_ms: float
    avg_confidence: float
    total_invocations: int


class QueueItem(BaseModel):
    id: int
    request_id: str
    customer_name: str
    order_number: str
    reason: str
    refund_amount: float
    fraud_score: Optional[float] = None
    status: str
    created_at: datetime


class EscalationResponse(BaseModel):
    id: int
    refund_request_id: int
    request_id: str
    customer_name: str
    order_number: str
    reason: str
    priority: str
    status: str
    assigned_to_name: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


class EscalationResolve(BaseModel):
    resolution_notes: str
    decision: str  # "approved" | "denied"
