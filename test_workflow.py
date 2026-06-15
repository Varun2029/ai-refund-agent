import asyncio
from app.graph.workflow import get_workflow

async def main():
    workflow = get_workflow()
    async for output in workflow.astream({
        'request_id': 'test-local-run',
        'customer_message': 'I received my order ORD-0001 today but it arrived completely shattered. It was a $120 glass vase. I want a refund.',
        'refund_id': 1
    }, config={'configurable': {'thread_id': 'test'}}):
        print(output)

if __name__ == '__main__':
    asyncio.run(main())
