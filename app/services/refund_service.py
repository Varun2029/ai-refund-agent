"""
Refund service — orchestrates the LangGraph workflow and persists results.

This is the bridge between the API layer and the agent pipeline.
"""

import uuid
import asyncio
from datetime import datetime, timezone
from typing import Optional, Callable

from sqlalchemy.orm import Session

from app.db.models import RefundRequest, AgentLog, Escalation, Order, Customer
from app.graph.workflow import get_workflow
from app.graph.state import RefundState


async def process_refund(
    db: Session,
    customer_message: str,
    customer_id: Optional[int] = None,
    order_number: Optional[str] = None,
    on_agent_log: Optional[Callable] = None,
) -> dict:
    """
    Run the full multi-agent refund pipeline.

    Parameters
    ----------
    db : Session
        Database session for persistence.
    customer_message : str
        The customer's natural language refund request.
    customer_id : int, optional
        Known customer ID (if authenticated).
    order_number : str, optional
        Order number if already known.
    on_agent_log : callable, optional
        Callback invoked after each agent completes, for real-time streaming.
        Signature: on_agent_log(log_entry: dict)

    Returns
    -------
    dict
        Final workflow state including decision, rationale, and all logs.
    """
    request_id = str(uuid.uuid4())

    # Build initial state
    initial_state: RefundState = {
        "request_id": request_id,
        "customer_message": customer_message,
        "extracted_order_number": order_number,
        "extracted_reason": None,
        "extracted_refund_amount": None,
        "intent": None,
        "customer_data": None,
        "order_data": None,
        "policy_result": None,
        "fraud_score": None,
        "fraud_flags": None,
        "fraud_reasoning": None,
        "decision": None,
        "decision_rationale": None,
        "agent_logs": [],
        "current_agent": "customer_agent",
        "error": None,
    }

    # ---- Run the workflow with streaming ----
    workflow = get_workflow()
    final_state = None

    async for event in workflow.astream(initial_state):
        for node_name, node_output in event.items():
            if isinstance(node_output, dict):
                # Merge node output into final_state
                if final_state is None:
                    final_state = dict(initial_state)
                final_state.update(node_output)

                # Stream new agent logs to callback
                if "agent_logs" in node_output and on_agent_log:
                    for log_entry in node_output["agent_logs"]:
                        try:
                            await on_agent_log(log_entry)
                        except Exception:
                            pass

    # Use initial state as fallback if something went wrong
    final_result = final_state or dict(initial_state)

    # ---- Persist to database ----
    order_data = final_result.get("order_data", {}) or {}
    customer_data = final_result.get("customer_data", {}) or {}

    # Resolve order_id and customer_id
    order_id = order_data.get("id")
    if not order_id and order_number:
        order = db.query(Order).filter(Order.order_number == order_number).first()
        if order:
            order_id = order.id
            customer_id = order.customer_id

    if not customer_id:
        customer_id = customer_data.get("id")

    # If we still don't have IDs, try to find them
    if not order_id:
        extracted_order = final_result.get("extracted_order_number")
        if extracted_order:
            order = db.query(Order).filter(Order.order_number == extracted_order).first()
            if order and (not customer_id or order.customer_id == customer_id):
                order_id = order.id
                if not customer_id:
                    customer_id = order.customer_id

    # If no order and no customer, default to 1 (anonymous demo)
    if not order_id and not customer_id:
        order = db.query(Order).first()
        if order:
            order_id = order.id
            customer_id = order.customer_id

    refund_amount = (
        final_result.get("extracted_refund_amount")
        or order_data.get("amount")
        or 0.0
    )

    # Create refund request record
    refund = RefundRequest(
        order_id=order_id,
        customer_id=customer_id or 1,
        request_id=request_id,
        reason=final_result.get("extracted_reason", customer_message),
        refund_amount=refund_amount,
        status=final_result.get("decision", "escalated"),
        fraud_score=final_result.get("fraud_score"),
        policy_check=final_result.get("policy_result", {}).get("eligible", "review") if final_result.get("policy_result") else None,
        decision_rationale=final_result.get("decision_rationale"),
        agent_workflow_state={
            "intent": final_result.get("intent"),
            "fraud_flags": final_result.get("fraud_flags"),
            "policy_result": final_result.get("policy_result"),
        },
        created_at=datetime.now(timezone.utc),
        resolved_at=datetime.now(timezone.utc) if final_result.get("decision") in ("approved", "denied") else None,
    )
    db.add(refund)
    db.flush()

    # Persist agent logs
    for log_entry in final_result.get("agent_logs", []):
        agent_log = AgentLog(
            refund_request_id=refund.id,
            agent_name=log_entry.get("agent_name", "unknown"),
            action=log_entry.get("action", ""),
            input_data={"summary": log_entry.get("input_summary", "")},
            output_data={"summary": log_entry.get("output_summary", "")},
            reasoning=log_entry.get("reasoning", ""),
            confidence=log_entry.get("confidence"),
            duration_ms=log_entry.get("duration_ms"),
        )
        db.add(agent_log)

    # Create escalation if needed
    if final_result.get("decision") == "escalated":
        escalation = Escalation(
            refund_request_id=refund.id,
            assigned_to=None,  # unassigned initially
            reason=final_result.get("decision_rationale", "Requires human review"),
            priority=_compute_priority(final_result.get("fraud_score", 50)),
            status="open",
        )
        db.add(escalation)

    db.commit()
    db.refresh(refund)

    # Trigger email notification
    customer = db.query(Customer).filter(Customer.id == refund.customer_id).first()
    if customer and customer.email:
        from app.services.email_service import send_refund_decision_email
        import asyncio
        email_decision = final_result.get("decision", "escalated")
        email_rationale = final_result.get("customer_message_out", final_result.get("decision_rationale", "Your request has been processed."))
        asyncio.create_task(send_refund_decision_email(customer.email, customer.name, email_decision, email_rationale))

    return {
        "request_id": request_id,
        "refund_id": refund.id,
        "decision": final_result.get("decision", "escalated"),
        "decision_rationale": final_result.get("decision_rationale", ""),
        "final_message": final_result.get("customer_message_out", "Your request has been processed."),
        "fraud_score": final_result.get("fraud_score"),
        "policy_check": final_result.get("policy_result", {}).get("eligible") if final_result.get("policy_result") else None,
        "agent_logs": final_result.get("agent_logs", []),
        "status": final_result.get("decision", "escalated"),
    }


def _compute_priority(fraud_score: float) -> str:
    """Map fraud score to escalation priority."""
    if fraud_score >= 80:
        return "critical"
    elif fraud_score >= 60:
        return "high"
    elif fraud_score >= 40:
        return "medium"
    return "low"
