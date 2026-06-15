"""
Customer Agent — first in the pipeline.

Responsibilities:
- Parse the customer's natural language message
- Extract: intent, order number, refund reason, requested amount
- Validate that the message is a refund-related request
"""

import json
import time
import asyncio
from app.graph.state import RefundState
from app.services.llm_provider import get_llm


SYSTEM_PROMPT = """You are a Customer Support Intake Agent for an e-commerce platform.
Your job is to analyze the customer's message and extract structured information.

You MUST respond with valid JSON containing these fields:
{
    "intent": "refund" | "inquiry" | "complaint" | "other",
    "order_number": "the order number mentioned (e.g. ORD-0001) or null if not mentioned",
    "reason": "concise summary of why the customer wants a refund",
    "refund_amount": null or the specific dollar amount if mentioned,
    "confidence": 0.0 to 1.0 indicating how confident you are in the extraction,
    "reasoning": "brief explanation of your analysis"
}

Rules:
- Look for order numbers in formats like ORD-XXXX, #XXXX, order XXXX
- If no order number is found, set it to null
- Classify intent carefully — only use "refund" if the customer clearly wants money back
- Explain your reasoning in 1-2 simple, non-technical sentences that a layman can understand. Do not use technical jargon or database terms."""


async def customer_agent(state: RefundState) -> dict:
    """Parse customer message, extract intent and order details."""
    start = time.time()
    llm = get_llm()
    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = await llm.chat(
                prompt=f"Analyze this customer message:\n\n\"{state['customer_message']}\"",
                system_prompt=SYSTEM_PROMPT,
                temperature=0.1,
                json_mode=True,
            )

            result = json.loads(response.content)
            duration_ms = int((time.time() - start) * 1000)

            log_entry = {
                "agent_name": "customer_agent",
                "action": "message_analysis",
                "input_summary": state["customer_message"][:200],
                "output_summary": f"Understood as a {result.get('intent')} request. Order: {result.get('order_number') or 'Not specified'}.",
                "reasoning": result.get("reasoning", ""),
                "confidence": result.get("confidence", 0.8),
                "duration_ms": duration_ms,
            }

            return {
                "intent": result.get("intent", "other"),
                "extracted_order_number": result.get("order_number"),
                "extracted_reason": result.get("reason", state["customer_message"]),
                "extracted_refund_amount": result.get("refund_amount"),
                "current_agent": "crm_agent",
                "agent_logs": [log_entry],
            }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[Customer Agent] Attempt {attempt + 1} failed: {e}", exc_info=True)
            
            if attempt < max_retries - 1:
                # We will log a retry action to the terminal, and wait a bit
                logger.info(f"Retrying customer_agent... ({attempt + 1}/{max_retries})")
                await asyncio.sleep(1)
                continue
            
            duration_ms = int((time.time() - start) * 1000)
            return {
                "intent": "refund",
                "extracted_reason": state["customer_message"],
                "current_agent": "crm_agent",
                "error": f"Customer agent error after {max_retries} attempts: {str(e)}",
                "agent_logs": [{
                    "agent_name": "customer_agent",
                    "action": "message_analysis_retry_failed",
                    "input_summary": state["customer_message"][:200],
                    "output_summary": f"Error: {str(e)}",
                    "reasoning": "Fallback — LLM failed after retries",
                    "confidence": 0.3,
                    "duration_ms": duration_ms,
                }],
            }
