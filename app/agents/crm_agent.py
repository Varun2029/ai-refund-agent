"""
CRM Agent — second in the pipeline.

Responsibilities:
- Look up customer profile from PostgreSQL
- Look up order details
- Enrich state with customer tier, order history, delivery status
- No LLM needed — pure database lookup
"""

import time
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Customer, Order
from app.graph.state import RefundState


async def crm_agent(state: RefundState) -> dict:
    """Look up customer and order data from the CRM database."""
    start = time.time()
    db: Session = SessionLocal()

    try:
        order_number = state.get("extracted_order_number")
        customer_data = None
        order_data = None

        if order_number:
            # Look up order by order number
            query = db.query(Order).filter(Order.order_number == order_number)
            if state.get("customer_id"):
                query = query.filter(Order.customer_id == state["customer_id"])
            order = query.first()
            
            if order:
                customer = db.query(Customer).filter(Customer.id == order.customer_id).first()

                order_data = {
                    "id": order.id,
                    "order_number": order.order_number,
                    "amount": order.amount,
                    "status": order.status,
                    "items": order.items or [],
                    "order_date": order.order_date.isoformat() if order.order_date else None,
                    "delivered_date": order.delivered_date.isoformat() if order.delivered_date else None,
                }

                if customer:
                    # Count historical refunds
                    refund_count = len(customer.refund_requests) if customer.refund_requests else 0

                    customer_data = {
                        "id": customer.id,
                        "name": customer.name,
                        "email": customer.email,
                        "phone": customer.phone,
                        "tier": customer.tier,
                        "total_orders": customer.total_orders,
                        "total_spent": customer.total_spent,
                        "account_age_days": (
                            (time.time() - customer.created_at.timestamp())
                            / 86400
                            if customer.created_at
                            else 0
                        ),
                        "refund_count": refund_count,
                    }

        duration_ms = int((time.time() - start) * 1000)
        found = order_data is not None

        log_entry = {
            "agent_name": "crm_agent",
            "action": "database_lookup",
            "input_summary": f"order_number={order_number}",
            "output_summary": (
                f"Successfully located order and account history."
                if found
                else f"Could not locate order {order_number} in our records."
            ),
            "reasoning": (
                f"I checked the records. This is a {customer_data['tier'] if customer_data else 'new'} customer who has placed {customer_data['total_orders'] if customer_data else 0} previous orders. I also noticed they have requested {customer_data['refund_count'] if customer_data else 0} refunds in the past."
                if found
                else "I couldn't find an order matching that number for your account."
            ),
            "confidence": 1.0 if found else 0.0,
            "duration_ms": duration_ms,
        }

        return {
            "customer_data": customer_data,
            "order_data": order_data,
            "current_agent": "policy_agent",
            "agent_logs": [log_entry],
        }

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        return {
            "current_agent": "policy_agent",
            "error": f"CRM agent error: {str(e)}",
            "agent_logs": [{
                "agent_name": "crm_agent",
                "action": "database_lookup",
                "input_summary": f"order_number={state.get('extracted_order_number')}",
                "output_summary": f"Error: {str(e)}",
                "reasoning": "Database lookup failed",
                "confidence": 0.0,
                "duration_ms": duration_ms,
            }],
        }
    finally:
        db.close()
