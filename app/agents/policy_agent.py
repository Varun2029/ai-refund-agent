"""
Policy Agent — third in the pipeline.

Responsibilities:
- Query the RAG policy store with the refund reason
- Use LLM to evaluate whether the refund request complies with policy
- Return pass / fail / review verdict
"""

import json
import time
from app.graph.state import RefundState
from app.services.llm_provider import get_llm
from app.rag.policy_store import PolicyStore


SYSTEM_PROMPT = """You are a Refund Policy Compliance Agent for an e-commerce platform.

You have been given relevant excerpts from the company's refund policies and details about a refund request.
Your job is to determine whether the refund request complies with company policy.

You MUST respond with valid JSON:
{
    "eligible": true | false | "review",
    "reason": "clear explanation of why the refund is or isn't eligible",
    "matched_policies": ["list of relevant policy sections that apply"],
    "conditions": ["any conditions that must be met for the refund"],
    "confidence": 0.0 to 1.0
}

Rules:
- "eligible": true means the refund clearly complies with policy
- "eligible": false means the refund clearly violates policy
- "eligible": "review" means the case is ambiguous and needs human review
- Always cite specific policy sections in your reasoning
- If no order data is available, set eligible to "review"
- Consider the customer's tier (gold customers get more lenient treatment)
- Explain your reasoning in 1-2 simple, non-technical sentences that a layman can understand. Do not use technical jargon or database terms."""


async def policy_agent(state: RefundState) -> dict:
    """Validate refund request against company policies using RAG."""
    start = time.time()
    llm = get_llm()

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Query RAG for relevant policy chunks
            reason = state.get("extracted_reason", "")
            store = PolicyStore.get_instance()
            policy_chunks = store.query(reason, top_k=5)

            policy_context = "\n\n---\n\n".join(
                f"[Source: {chunk['source']}] (relevance: {chunk['score']:.2f})\n{chunk['text']}"
                for chunk in policy_chunks
            )

            # Build context from state
            order_data = state.get("order_data", {}) or {}
            customer_data = state.get("customer_data", {}) or {}

            prompt = f"""Evaluate this refund request against company policy.

    ## Refund Request
    - Reason: {reason}
    - Requested Amount: ${state.get('extracted_refund_amount') or order_data.get('amount', 'N/A')}
    - Order Number: {state.get('extracted_order_number', 'N/A')}
    - Order Status: {order_data.get('status', 'N/A')}
    - Order Date: {order_data.get('order_date', 'N/A')}
    - Delivered Date: {order_data.get('delivered_date', 'N/A')}
    - Customer Tier: {customer_data.get('tier', 'N/A')}
    - Items: {json.dumps(order_data.get('items', []))}

    ## Relevant Company Policies
    {policy_context}

    Determine if this refund is eligible per company policy."""

            response = await llm.chat(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.1,
                json_mode=True,
            )

            result = json.loads(response.content)
            duration_ms = int((time.time() - start) * 1000)

            # Normalize eligible to string
            eligible = result.get("eligible", "review")
            if isinstance(eligible, bool):
                policy_check = "pass" if eligible else "fail"
            else:
                policy_check = str(eligible) if eligible in ("pass", "fail", "review") else "review"
                if eligible is True:
                    policy_check = "pass"
                elif eligible is False:
                    policy_check = "fail"

            log_entry = {
                "agent_name": "policy_agent",
                "action": "policy_validation",
                "input_summary": f"reason='{reason[:100]}', order={state.get('extracted_order_number')}",
                "output_summary": f"Policy verification: {policy_check.title()}. Evaluated against {len(result.get('matched_policies', []))} related policies.",
                "reasoning": result.get("reason", ""),
                "confidence": result.get("confidence", 0.7),
                "duration_ms": duration_ms,
            }

            return {
                "policy_result": {
                    "eligible": policy_check,
                    "reason": result.get("reason", ""),
                    "matched_policies": result.get("matched_policies", []),
                    "conditions": result.get("conditions", []),
                },
                "current_agent": "fraud_agent",
                "agent_logs": [log_entry],
            }

        except Exception as e:
            import logging
            import asyncio
            logger = logging.getLogger(__name__)
            logger.error(f"[Policy Agent] Attempt {attempt + 1} failed: {e}", exc_info=True)
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying policy_agent... ({attempt + 1}/{max_retries})")
                await asyncio.sleep(1)
                continue
                
            duration_ms = int((time.time() - start) * 1000)
            return {
                "policy_result": {"eligible": "review", "reason": f"Policy check error: {str(e)}"},
                "current_agent": "fraud_agent",
                "error": f"Policy agent error after {max_retries} attempts: {str(e)}",
                "agent_logs": [{
                    "agent_name": "policy_agent",
                    "action": "policy_validation_retry_failed",
                    "input_summary": f"reason='{state.get('extracted_reason', '')[:100]}'",
                    "output_summary": f"Error: {str(e)}",
                    "reasoning": "Fallback to review due to policy check failure",
                    "confidence": 0.0,
                    "duration_ms": duration_ms,
                }],
            }
