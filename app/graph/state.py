"""
LangGraph workflow state schema.

The RefundState TypedDict flows through all 5 agents in the pipeline.
Each agent reads from and writes to specific fields.
"""

from typing import TypedDict, Optional, Annotated
from operator import add


class AgentLogEntry(TypedDict):
    """Single agent reasoning log entry."""
    agent_name: str
    action: str
    input_summary: str
    output_summary: str
    reasoning: str
    confidence: float
    duration_ms: int


class RefundState(TypedDict):
    """Shared state flowing through the multi-agent refund pipeline."""

    # --- Request info ---
    request_id: str
    customer_message: str

    # --- Extracted by Customer Agent ---
    extracted_order_number: Optional[str]
    extracted_reason: Optional[str]
    extracted_refund_amount: Optional[float]
    intent: Optional[str]  # "refund" | "inquiry" | "complaint" | "other"

    # --- Enriched by CRM Agent ---
    customer_data: Optional[dict]
    order_data: Optional[dict]

    # --- Policy Agent output ---
    policy_result: Optional[dict]  # {eligible: bool, reason: str, matched_policies: list}

    # --- Fraud Agent output ---
    fraud_score: Optional[float]  # 0-100
    fraud_flags: Optional[list[str]]
    fraud_reasoning: Optional[str]

    # --- Decision Agent output ---
    decision: Optional[str]  # "approved" | "denied" | "escalated"
    decision_rationale: Optional[str]

    # --- Workflow metadata ---
    agent_logs: Annotated[list[dict], add]  # append-only via reducer
    current_agent: str
    error: Optional[str]
