"""
Seed script — creates demo admin user + sample customers/orders.
Run from the project root: python seed.py
"""
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath("."))

from app.db.database import SessionLocal, engine, Base
from app.db.models import User, Customer, Order
from app.services.auth_service import hash_password

Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    try:
        # ── Admin user ────────────────────────────────────────────────────────
        if not db.query(User).filter(User.email == "admin@refundai.com").first():
            db.add(User(
                full_name="Admin User",
                email="admin@refundai.com",
                password_hash=hash_password("admin123"),
                role="admin",
            ))
            db.commit()
            print("[OK] Created admin user: admin@refundai.com / admin123")
        else:
            print("[SKIP] Admin user already exists")

        # ── Demo customers ────────────────────────────────────────────────────
        customers_data = [
            {"name": "Alice Johnson", "email": "alice@example.com", "phone": "555-0101", "tier": "gold",   "total_orders": 15, "total_spent": 2340.50},
            {"name": "Bob Smith",     "email": "bob@example.com",   "phone": "555-0102", "tier": "silver", "total_orders": 7,  "total_spent": 890.00},
            {"name": "Carol Davis",   "email": "carol@example.com", "phone": "555-0103", "tier": "bronze", "total_orders": 2,  "total_spent": 145.00},
        ]
        customers = []
        for cd in customers_data:
            c = db.query(Customer).filter(Customer.email == cd["email"]).first()
            if not c:
                c = Customer(**cd)
                db.add(c)
                db.commit()
                db.refresh(c)
                print(f"[OK] Created customer: {cd['name']}")
            else:
                print(f"[SKIP] Customer already exists: {cd['name']}")
            customers.append(c)

        # ── Demo orders ───────────────────────────────────────────────────────
        now = datetime.now(timezone.utc)
        orders_data = [
            {"customer": customers[0], "order_number": "ORD-1001", "amount": 299.99, "status": "delivered", "items": [{"name": "Wireless Headphones", "qty": 1, "price": 299.99}],   "order_date": now - timedelta(days=30), "delivered_date": now - timedelta(days=25)},
            {"customer": customers[0], "order_number": "ORD-1002", "amount": 89.50,  "status": "delivered", "items": [{"name": "Phone Case", "qty": 2, "price": 44.75}],              "order_date": now - timedelta(days=10), "delivered_date": now - timedelta(days=7)},
            {"customer": customers[1], "order_number": "ORD-1003", "amount": 549.00, "status": "delivered", "items": [{"name": "Smart Watch", "qty": 1, "price": 549.00}],            "order_date": now - timedelta(days=60), "delivered_date": now - timedelta(days=55)},
            {"customer": customers[1], "order_number": "ORD-1004", "amount": 34.99,  "status": "delivered", "items": [{"name": "USB Cable Pack", "qty": 1, "price": 34.99}],          "order_date": now - timedelta(days=5),  "delivered_date": now - timedelta(days=3)},
            {"customer": customers[2], "order_number": "ORD-1005", "amount": 145.00, "status": "delivered", "items": [{"name": "Bluetooth Speaker", "qty": 1, "price": 145.00}],      "order_date": now - timedelta(days=45), "delivered_date": now - timedelta(days=40)},
        ]
        for od in orders_data:
            if not db.query(Order).filter(Order.order_number == od["order_number"]).first():
                customer = od.pop("customer")
                o = Order(customer_id=customer.id, **od)
                db.add(o)
                db.commit()
                print(f"[OK] Created order: {od['order_number']}")
            else:
                print(f"[SKIP] Order already exists: {od['order_number']}")

        print("\n[DONE] Database seeded! Login: admin@refundai.com / admin123")
        print("[INFO] Demo orders: ORD-1001, ORD-1002, ORD-1003, ORD-1004, ORD-1005")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
