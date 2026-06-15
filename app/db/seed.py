"""
Seed script — populates the database with demo data.

Run: python -m app.db.seed

Creates:
- 3 platform users (admin, manager, agent)
- 15 customers across gold/silver/bronze tiers
- 35 orders with realistic items and dates
- 8 historical refund requests with mixed outcomes
"""

import uuid
import random
from datetime import datetime, timedelta, timezone

from app.db.database import engine, SessionLocal, Base
from app.db.models import User, Customer, Order, RefundRequest, AgentLog, Escalation
from app.services.auth_service import hash_password


def seed():
    """Drop + recreate all tables, then insert demo data."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        _seed_users(db)
        _seed_customers_and_orders(db)
        _seed_historical_refunds(db)
        db.commit()
        print("[OK] Database seeded successfully!")
        print(f"   • 3 users")
        print(f"   • 15 customers")
        print(f"   • 35 orders")
        print(f"   • 8 historical refund requests")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed failed: {e}")
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def _seed_users(db):
    users = [
        User(
            email="admin@refundai.com",
            password_hash=hash_password("admin123"),
            role="admin",
            full_name="Alex Admin",
        ),
        User(
            email="manager@refundai.com",
            password_hash=hash_password("manager123"),
            role="manager",
            full_name="Morgan Manager",
        ),
        User(
            email="agent@refundai.com",
            password_hash=hash_password("agent123"),
            role="agent",
            full_name="Sam Agent",
        ),
    ]
    db.add_all(users)
    db.flush()


# ---------------------------------------------------------------------------
# Customers + Orders
# ---------------------------------------------------------------------------

_ITEMS_CATALOG = [
    {"name": "Wireless Noise-Cancelling Headphones", "price": 249.99, "sku": "ELEC-001"},
    {"name": "Premium Yoga Mat", "price": 89.99, "sku": "FIT-001"},
    {"name": "Organic Coffee Beans (2lb)", "price": 34.99, "sku": "FOOD-001"},
    {"name": "Leather Laptop Sleeve 15\"", "price": 59.99, "sku": "ACC-001"},
    {"name": "Smart Watch Pro", "price": 399.99, "sku": "ELEC-002"},
    {"name": "Stainless Steel Water Bottle", "price": 29.99, "sku": "HOME-001"},
    {"name": "Running Shoes V2", "price": 129.99, "sku": "FIT-002"},
    {"name": "Bluetooth Speaker Mini", "price": 79.99, "sku": "ELEC-003"},
    {"name": "Ceramic Plant Pot Set", "price": 44.99, "sku": "HOME-002"},
    {"name": "Ergonomic Mouse", "price": 69.99, "sku": "ELEC-004"},
    {"name": "Bamboo Cutting Board", "price": 24.99, "sku": "HOME-003"},
    {"name": "Resistance Band Set", "price": 19.99, "sku": "FIT-003"},
    {"name": "Espresso Machine", "price": 599.99, "sku": "HOME-004"},
    {"name": "Ultra HD Webcam", "price": 149.99, "sku": "ELEC-005"},
    {"name": "Memory Foam Pillow", "price": 39.99, "sku": "HOME-005"},
]

_CUSTOMER_DATA = [
    # (name, email, phone, tier)
    ("Emma Johnson", "emma.j@email.com", "+1-555-0101", "gold"),
    ("Liam Chen", "liam.chen@email.com", "+1-555-0102", "gold"),
    ("Sophia Rodriguez", "sophia.r@email.com", "+1-555-0103", "gold"),
    ("Noah Williams", "noah.w@email.com", "+1-555-0104", "silver"),
    ("Olivia Brown", "olivia.b@email.com", "+1-555-0105", "silver"),
    ("James Garcia", "james.g@email.com", "+1-555-0106", "silver"),
    ("Ava Martinez", "ava.m@email.com", "+1-555-0107", "silver"),
    ("William Davis", "will.d@email.com", "+1-555-0108", "silver"),
    ("Isabella Wilson", "izzy.w@email.com", "+1-555-0109", "bronze"),
    ("Benjamin Taylor", "ben.t@email.com", "+1-555-0110", "bronze"),
    ("Mia Anderson", "mia.a@email.com", "+1-555-0111", "bronze"),
    ("Lucas Thomas", "lucas.t@email.com", "+1-555-0112", "bronze"),
    ("Charlotte Lee", "charlotte.l@email.com", "+1-555-0113", "bronze"),
    ("Henry Harris", "henry.h@email.com", "+1-555-0114", "bronze"),
    ("Amelia Clark", "amelia.c@email.com", "+1-555-0115", "bronze"),
]


def _seed_customers_and_orders(db):
    now = datetime.now(timezone.utc)
    random.seed(42)  # reproducible data

    order_counter = 1
    for idx, (name, email, phone, tier) in enumerate(_CUSTOMER_DATA):
        # Determine order count by tier
        if tier == "gold":
            n_orders = random.randint(4, 6)
        elif tier == "silver":
            n_orders = random.randint(2, 4)
        else:
            n_orders = random.randint(1, 2)

        total_spent = 0.0
        customer = Customer(
            name=name,
            email=email,
            phone=phone,
            tier=tier,
            total_orders=n_orders,
            total_spent=0,  # updated below
            created_at=now - timedelta(days=random.randint(90, 365)),
        )
        db.add(customer)
        db.flush()

        for j in range(n_orders):
            items_count = random.randint(1, 3)
            selected_items = random.sample(_ITEMS_CATALOG, items_count)
            amount = round(sum(item["price"] for item in selected_items), 2)
            total_spent += amount

            order_date = now - timedelta(days=random.randint(5, 120))
            status = random.choice(["delivered", "delivered", "delivered", "shipped"])
            delivered_date = (
                order_date + timedelta(days=random.randint(2, 7))
                if status == "delivered"
                else None
            )

            order = Order(
                customer_id=customer.id,
                order_number=f"ORD-{order_counter:04d}",
                amount=amount,
                status=status,
                items=[{"name": i["name"], "price": i["price"], "sku": i["sku"]} for i in selected_items],
                order_date=order_date,
                delivered_date=delivered_date,
            )
            db.add(order)
            order_counter += 1

        customer.total_spent = round(total_spent, 2)
        db.flush()


# ---------------------------------------------------------------------------
# Historical refund requests (for dashboard analytics)
# ---------------------------------------------------------------------------

_REFUND_REASONS = [
    "Product arrived damaged — cracked screen",
    "Wrong item received, ordered headphones but got a speaker",
    "Item stopped working after 3 days",
    "Never received the package, tracking shows delivered",
    "Duplicate charge on my card",
    "Product doesn't match the description on the website",
    "Changed my mind, want to return within 30 days",
    "Received used/opened product instead of new",
]


def _seed_historical_refunds(db):
    now = datetime.now(timezone.utc)
    random.seed(99)

    orders = db.query(Order).filter(Order.status == "delivered").limit(8).all()

    statuses = ["approved", "approved", "approved", "denied", "denied", "escalated", "escalated", "approved"]
    fraud_scores = [12.5, 8.0, 22.3, 65.0, 45.0, 78.5, 82.0, 5.0]

    for i, order in enumerate(orders):
        req_status = statuses[i]
        fraud_score = fraud_scores[i]
        policy_check = "pass" if fraud_score < 50 else ("review" if fraud_score < 75 else "fail")
        if req_status == "approved":
            policy_check = "pass"
        elif req_status == "denied":
            policy_check = "fail"

        refund = RefundRequest(
            order_id=order.id,
            customer_id=order.customer_id,
            request_id=str(uuid.uuid4()),
            reason=_REFUND_REASONS[i],
            refund_amount=order.amount,
            status=req_status,
            fraud_score=fraud_score,
            policy_check=policy_check,
            decision_rationale=f"Auto-processed: fraud_score={fraud_score}, policy={policy_check}",
            created_at=now - timedelta(days=random.randint(1, 30)),
            resolved_at=now - timedelta(days=random.randint(0, 5)) if req_status != "escalated" else None,
        )
        db.add(refund)
        db.flush()

        # Add agent logs for each historical refund
        agents = ["customer_agent", "crm_agent", "policy_agent", "fraud_agent", "decision_agent"]
        for j, agent_name in enumerate(agents):
            log = AgentLog(
                refund_request_id=refund.id,
                agent_name=agent_name,
                action=f"{agent_name}_analysis",
                reasoning=f"Processed by {agent_name} — {'passed' if j < 3 else 'flagged'} checks",
                confidence=round(random.uniform(0.7, 0.99), 2),
                duration_ms=random.randint(200, 2000),
                created_at=refund.created_at + timedelta(seconds=j * 2),
            )
            db.add(log)

        # Add escalation for escalated refunds
        if req_status == "escalated":
            esc = Escalation(
                refund_request_id=refund.id,
                assigned_to=2,  # manager user
                reason=f"High fraud score ({fraud_score}) requires manual review",
                priority="high" if fraud_score > 80 else "medium",
                status="open",
                created_at=refund.created_at,
            )
            db.add(esc)


if __name__ == "__main__":
    seed()
