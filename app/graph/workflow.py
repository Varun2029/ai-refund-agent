"""
LangGraph StateGraph — defines the multi-agent refund processing pipeline.

Pipeline: Customer Agent → CRM Agent → Policy Agent → Fraud Agent → Decision Agent

The graph is compiled once and re-used for every refund request.
"""

from langgraph.graph import StateGraph, END

from app.graph.state import RefundState
from app.agents.customer_agent import customer_agent
from app.agents.crm_agent import crm_agent
from app.agents.policy_agent import policy_agent
from app.agents.fraud_agent import fraud_agent
from app.agents.decision_agent import decision_agent


def build_workflow() -> StateGraph:
    """Construct and compile the refund processing workflow graph."""

    graph = StateGraph(RefundState)

    # ---- Add agent nodes ----
    graph.add_node("customer_agent", customer_agent)
    graph.add_node("crm_agent", crm_agent)
    graph.add_node("policy_agent", policy_agent)
    graph.add_node("fraud_agent", fraud_agent)
    graph.add_node("decision_agent", decision_agent)

    # ---- Define edges (linear pipeline) ----
    graph.set_entry_point("customer_agent")
    graph.add_edge("customer_agent", "crm_agent")
    graph.add_edge("crm_agent", "policy_agent")
    graph.add_edge("policy_agent", "fraud_agent")
    graph.add_edge("fraud_agent", "decision_agent")
    graph.add_edge("decision_agent", END)

    return graph.compile()


# Singleton compiled graph
_workflow = None


def get_workflow():
    """Return the compiled workflow (lazy-initialized singleton)."""
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
    return _workflow
