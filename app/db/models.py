"""
SQLAlchemy ORM models — 6 tables.

Tables
------
- users          : platform operators (admin / manager / agent)
- customers      : e-commerce customers
- orders         : customer orders
- refund_requests: refund lifecycle tracking
- agent_logs     : per-agent reasoning logs
- escalations    : human-review escalation records
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


# ---------------------------------------------------------------------------
# Users (platform operators)
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="agent")  # admin | manager | agent
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    escalations = relationship("Escalation", back_populates="assigned_user")


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50))
    tier = Column(String(50), default="bronze")  # gold | silver | bronze
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="customer")
    refund_requests = relationship("RefundRequest", back_populates="customer")


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="delivered")  # delivered | shipped | processing | cancelled
    items = Column(JSON)  # JSON array of item dicts
    order_date = Column(DateTime(timezone=True), nullable=False)
    delivered_date = Column(DateTime(timezone=True))

    customer = relationship("Customer", back_populates="orders")
    refund_requests = relationship("RefundRequest", back_populates="order")


# ---------------------------------------------------------------------------
# Refund Requests
# ---------------------------------------------------------------------------
class RefundRequest(Base):
    __tablename__ = "refund_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    request_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    reason = Column(Text, nullable=False)
    refund_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")  # pending | processing | approved | denied | escalated
    fraud_score = Column(Float)
    policy_check = Column(String(50))  # pass | fail | review
    decision_rationale = Column(Text)
    agent_workflow_state = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

    order = relationship("Order", back_populates="refund_requests")
    customer = relationship("Customer", back_populates="refund_requests")
    agent_logs = relationship("AgentLog", back_populates="refund_request", order_by="AgentLog.created_at")
    escalation = relationship("Escalation", back_populates="refund_request", uselist=False)


# ---------------------------------------------------------------------------
# Agent Logs (per-agent reasoning trace)
# ---------------------------------------------------------------------------
class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    refund_request_id = Column(Integer, ForeignKey("refund_requests.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    reasoning = Column(Text)
    confidence = Column(Float)
    duration_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    refund_request = relationship("RefundRequest", back_populates="agent_logs")


# ---------------------------------------------------------------------------
# Escalations (human-review queue)
# ---------------------------------------------------------------------------
class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, index=True)
    refund_request_id = Column(Integer, ForeignKey("refund_requests.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason = Column(Text, nullable=False)
    priority = Column(String(50), default="medium")  # low | medium | high | critical
    status = Column(String(50), default="open")  # open | in_review | resolved
    resolution_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

    refund_request = relationship("RefundRequest", back_populates="escalation")
    assigned_user = relationship("User", back_populates="escalations")
