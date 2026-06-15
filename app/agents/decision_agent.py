"""
Decision Agent — fifth and final in the pipeline.

Responsibilities:
- Synthesize all signals: policy result, fraud score, customer data
- Make final decision: approve / deny / escalate
- Generate human-readable rationale
"""

import json
import time
from app.graph.state import RefundState
from app.services.llm_provider import get_llm


SYSTEM_PROMPT = """You are the Decision Agent for an e-commerce refund platform.
You make the FINAL decision on refund requests based on inputs from other agents.

Decision rules:
1. If fraud_score > 75 → ESCALATE (too risky for auto-decision)
2. If policy_check = "fail" AND fraud_score > 50 → DENY
3. If policy_check = "fail" AND fraud_score <= 50 → ESCALATE (policy violation but low fraud)
4. If policy_check = "pass" AND fraud_score < 30 → APPROVE
5. If policy_check = "pass" AND fraud_score 30-75 → ESCALATE (policy ok but fraud concerns)
6. If policy_check = "review" → ESCALATE (ambiguous case)
7. Gold tier customers with fraud_score < 50 and policy_check = "pass" → APPROVE (preferred treatment)

You MUST respond with valid JSON:
{
    "decision": "approved" | "denied" | "escalated",
    "rationale": "1-2 simple, non-technical sentences explaining the decision. Do not use jargon.",
    "confidence": 0.0 to 1.0,
    "summary": "One very short, polite, layman sentence to speak to the customer (e.g. 'Good news, your refund is approved.')"
}"""


async def decision_agent(state: RefundState) -> dict:
    """Make final refund decision based on all gathered signals."""
    start = time.time()
    llm = get_llm()

    fraud_score = state.get("fraud_score", 50) or 50
    policy_result = state.get("policy_result", {}) or {}
    policy_check = policy_result.get("eligible", "review")
    customer_data = state.get("customer_data", {}) or {}
    order_data = state.get("order_data", {}) or {}

    max_retries = 3
    for attempt in range(max_retries):
        try:
            prompt = f"""Make the final refund decision based on these inputs:

    ## Policy Check Result
    - Eligible: {policy_check}
    - Policy Reason: {policy_result.get('reason', 'N/A')}
    - Matched Policies: {json.dumps(policy_result.get('matched_policies', []))}

    ## Fraud Assessment
    - Fraud Score: {fraud_score}/100
    - Fraud Flags: {json.dumps(state.get('fraud_flags', []))}
    - Fraud Reasoning: {state.get('fraud_reasoning', 'N/A')}

    ## Customer Profile
    - Name: {customer_data.get('name', 'Unknown')}
    - Tier: {customer_data.get('tier', 'unknown')}
    - Total Orders: {customer_data.get('total_orders', 0)}
    - Total Spent: ${customer_data.get('total_spent', 0)}
    - Prior Refunds: {customer_data.get('refund_count', 0)}

    ## Refund Request
    - Reason: {state.get('extracted_reason', 'N/A')}
    - Amount: ${state.get('extracted_refund_amount') or order_data.get('amount', 'N/A')}
    - Order Status: {order_data.get('status', 'N/A')}

    Apply the decision rules and make your determination."""

            response = await llm.chat(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.1,
                json_mode=True,
            )

            result = json.loads(response.content)
            duration_ms = int((time.time() - start) * 1000)

            decision = result.get("decision", "escalated")
            if decision not in ("approved", "denied", "escalated"):
                decision = "escalated"

            log_entry = {
                "agent_name": "decision_agent",
                "action": "final_decision",
                "input_summary": f"fraud={fraud_score}, policy={policy_check}, tier={customer_data.get('tier', 'N/A')}",
                "output_summary": f"Reached final conclusion: {decision.title()}.",
                "reasoning": result.get("rationale", ""),
                "confidence": result.get("confidence", 0.7),
                "duration_ms": duration_ms,
            }

            return {
                "decision": decision,
                "decision_rationale": result.get("rationale", "Decision made by AI agent"),
                "customer_message_out": result.get("summary", "We have processed your request."),
                "current_agent": "complete",
                "agent_logs": [log_entry],
            }

        except Exception as e:
            import logging
            import asyncio
            logger = logging.getLogger(__name__)
            logger.error(f"[Decision Agent] Attempt {attempt + 1} failed: {e}", exc_info=True)
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying decision_agent... ({attempt + 1}/{max_retries})")
                await asyncio.sleep(1)
                continue
                
            duration_ms = int((time.time() - start) * 1000)

            # Fallback rule-based decision
            if fraud_score > 75:
                fallback_decision = "escalated"
            elif policy_check == "fail":
                fallback_decision = "denied"
            elif policy_check == "pass" and fraud_score < 30:
                fallback_decision = "approved"
            else:
                fallback_decision = "escalated"

            return {
                "decision": fallback_decision,
                "decision_rationale": f"Rule-based fallback (LLM unavailable after {max_retries} attempts): fraud={fraud_score}, policy={policy_check}",
                "current_agent": "complete",
                "error": f"Decision agent error: {str(e)}",
                "agent_logs": [{
                    "agent_name": "decision_agent",
                    "action": "final_decision_retry_failed",
                    "input_summary": f"fraud={fraud_score}, policy={policy_check}",
                    "output_summary": f"Fallback decision={fallback_decision}",
                    "reasoning": f"Rule-based fallback due to LLM error: {str(e)}",
                    "confidence": 0.5,
                    "duration_ms": duration_ms,
                }],
            }
