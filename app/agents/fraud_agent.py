"""
Fraud Agent — fourth in the pipeline.

Responsibilities:
- Compute a fraud risk score (0-100) based on multiple signals
- Flag suspicious patterns
- Use both rule-based heuristics and LLM analysis
"""

import json
import time
from app.graph.state import RefundState
from app.services.llm_provider import get_llm


SYSTEM_PROMPT = """You are a Fraud Detection Agent for an e-commerce refund platform.

Given customer data, order data, and the refund request details, assess the fraud risk.

Consider these factors:
1. Refund frequency — multiple refunds in a short period is suspicious
2. Refund-to-order ratio — high ratio of refunds to total orders
3. Account age — very new accounts requesting refunds are higher risk
4. Refund amount vs order amount — requesting more than the order value
5. Customer tier — gold/silver customers have established trust
6. Delivery status — refunds on undelivered items need different handling
7. Reason plausibility — vague or common fraud reasons

You MUST respond with valid JSON:
{
    "fraud_score": 0 to 100 (integer),
    "risk_level": "low" | "medium" | "high" | "critical",
    "flags": ["list of specific fraud indicators found"],
    "reasoning": "detailed explanation of the fraud assessment",
    "confidence": 0.0 to 1.0
}

Score guidelines:
- 0-30: Low risk — typical legitimate refund
- 31-60: Medium risk — some indicators present, but likely legitimate
- 61-80: High risk — multiple fraud indicators, recommend escalation
- 81-100: Critical risk — strong fraud pattern detected
- Explain your reasoning in 1-2 simple, non-technical sentences that a layman can understand. Do not use technical jargon or database terms."""


async def fraud_agent(state: RefundState) -> dict:
    """Compute fraud score using rules + LLM analysis."""
    start = time.time()
    llm = get_llm()

    customer_data = state.get("customer_data", {}) or {}
    order_data = state.get("order_data", {}) or {}

    # ---- Rule-based pre-score ----
    rule_score = 0
    rule_flags = []

    refund_count = customer_data.get("refund_count", 0)
    if refund_count >= 3:
        rule_score += 25
        rule_flags.append(f"High refund frequency: {refund_count} prior refunds")
    elif refund_count >= 2:
        rule_score += 10
        rule_flags.append(f"Moderate refund frequency: {refund_count} prior refunds")

    total_orders = customer_data.get("total_orders", 1) or 1
    if total_orders > 0 and refund_count / total_orders > 0.5:
        rule_score += 20
        rule_flags.append(f"High refund ratio: {refund_count}/{total_orders} orders refunded")

    account_age = customer_data.get("account_age_days", 365)
    if account_age < 30:
        rule_score += 15
        rule_flags.append(f"New account: {int(account_age)} days old")

    tier = customer_data.get("tier", "bronze")
    if tier == "gold":
        rule_score = max(0, rule_score - 15)
    elif tier == "silver":
        rule_score = max(0, rule_score - 5)

    refund_amount = state.get("extracted_refund_amount") or order_data.get("amount", 0)
    order_amount = order_data.get("amount", 0)
    if order_amount > 0 and refund_amount > order_amount:
        rule_score += 20
        rule_flags.append("Refund exceeds order amount")

    if not order_data:
        rule_score += 15
        rule_flags.append("Order not found in system")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # ---- LLM-based analysis ----
            prompt = f"""Assess fraud risk for this refund request.

    ## Rule-Based Pre-Score: {rule_score}/100
    ## Rule-Based Flags: {json.dumps(rule_flags)}

    ## Customer Profile
    - Name: {customer_data.get('name', 'Unknown')}
    - Tier: {customer_data.get('tier', 'unknown')}
    - Total Orders: {customer_data.get('total_orders', 'N/A')}
    - Total Spent: ${customer_data.get('total_spent', 'N/A')}
    - Account Age: {int(customer_data.get('account_age_days', 0))} days
    - Prior Refunds: {customer_data.get('refund_count', 0)}

    ## Order Details
    - Order Number: {order_data.get('order_number', 'N/A')}
    - Amount: ${order_data.get('amount', 'N/A')}
    - Status: {order_data.get('status', 'N/A')}
    - Items: {json.dumps(order_data.get('items', []))}

    ## Refund Request
    - Reason: {state.get('extracted_reason', 'N/A')}
    - Requested Amount: ${refund_amount}

    Factor in the rule-based pre-score. Provide your final fraud assessment."""

            response = await llm.chat(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.2,
                json_mode=True,
            )

            result = json.loads(response.content)
            duration_ms = int((time.time() - start) * 1000)

            # Blend rule score and LLM score
            llm_score = result.get("fraud_score", 50)
            final_score = round((rule_score * 0.4) + (llm_score * 0.6))
            final_score = max(0, min(100, final_score))

            all_flags = rule_flags + result.get("flags", [])

            log_entry = {
                "agent_name": "fraud_agent",
                "action": "fraud_assessment",
                "input_summary": f"customer={customer_data.get('name', 'N/A')}, amount=${refund_amount}",
                "output_summary": f"Security check completed. Risk assessed as {result.get('risk_level', 'unknown')}.",
                "reasoning": result.get("reasoning", ""),
                "confidence": result.get("confidence", 0.7),
                "duration_ms": duration_ms,
            }

            return {
                "fraud_score": final_score,
                "fraud_flags": all_flags,
                "fraud_reasoning": result.get("reasoning", ""),
                "current_agent": "decision_agent",
                "agent_logs": [log_entry],
            }

        except Exception as e:
            import logging
            import asyncio
            logger = logging.getLogger(__name__)
            logger.error(f"[Fraud Agent] Attempt {attempt + 1} failed: {e}", exc_info=True)
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying fraud_agent... ({attempt + 1}/{max_retries})")
                await asyncio.sleep(1)
                continue
                
            duration_ms = int((time.time() - start) * 1000)
            # Fallback to rule-based score only
            return {
                "fraud_score": min(rule_score, 100),
                "fraud_flags": rule_flags,
                "fraud_reasoning": f"LLM analysis failed after {max_retries} attempts, using rule-based score only: {str(e)}",
                "current_agent": "decision_agent",
                "agent_logs": [{
                    "agent_name": "fraud_agent",
                    "action": "fraud_assessment_retry_failed",
                    "input_summary": f"customer={customer_data.get('name', 'N/A')}",
                    "output_summary": f"Fallback score={rule_score}, error={str(e)}",
                    "reasoning": f"Using rule-based scoring only due to LLM error",
                    "confidence": 0.4,
                    "duration_ms": duration_ms,
                }],
            }
