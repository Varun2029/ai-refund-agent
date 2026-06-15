import asyncio
from app.db.database import SessionLocal
from app.services.refund_service import process_refund

async def test_workflow():
    db = SessionLocal()
    print("Running process_refund...")
    try:
        result = await process_refund(
            db=db,
            customer_message="I want a refund for my broken headphones on order ORD-1001",
            customer_id=1,
            order_number="ORD-1001",
        )
        print("Workflow result:", result)
    except Exception as e:
        print("Workflow ERROR:", e)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_workflow())
