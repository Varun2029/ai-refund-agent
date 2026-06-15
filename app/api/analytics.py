"""
Analytics API routes — refund time series, fraud distribution, agent performance.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from app.db.database import get_db
from app.db.models import RefundRequest, AgentLog, User
from app.schemas.analytics import RefundTimeSeries, FraudDistribution, AgentPerformanceMetric
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/refunds", response_model=list[RefundTimeSeries])
def get_refund_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get refund volume time series data grouped by date."""
    from sqlalchemy import text
    
    rows = db.execute(
        text("""
        SELECT DATE(created_at) as date, status, COUNT(id) as count 
        FROM refund_requests 
        GROUP BY DATE(created_at), status
        ORDER BY DATE(created_at)
        """)
    ).all()

    # Pivot by date
    date_map: dict[str, dict] = {}
    for row in rows:
        date_str = str(row.date)
        if date_str not in date_map:
            date_map[date_str] = {"date": date_str, "approved": 0, "denied": 0, "escalated": 0, "pending": 0}
        status = row.status
        if status in date_map[date_str]:
            date_map[date_str][status] = row.count
        elif status == "processing":
            date_map[date_str]["pending"] += row.count

    return [RefundTimeSeries(**v) for v in sorted(date_map.values(), key=lambda x: x["date"])]


@router.get("/fraud", response_model=list[FraudDistribution])
def get_fraud_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get fraud score distribution as histogram buckets."""
    refunds = (
        db.query(RefundRequest.fraud_score)
        .filter(RefundRequest.fraud_score.isnot(None))
        .all()
    )

    # Bucket into 10-point ranges
    buckets = {f"{i}-{i+10}": 0 for i in range(0, 100, 10)}
    for (score,) in refunds:
        bucket_idx = min(int(score // 10) * 10, 90)
        key = f"{bucket_idx}-{bucket_idx + 10}"
        buckets[key] = buckets.get(key, 0) + 1

    return [
        FraudDistribution(range_label=k, count=v)
        for k, v in buckets.items()
    ]


@router.get("/agents", response_model=list[AgentPerformanceMetric])
def get_agent_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get average performance metrics per agent."""
    rows = (
        db.query(
            AgentLog.agent_name,
            func.avg(AgentLog.duration_ms).label("avg_duration"),
            func.avg(AgentLog.confidence).label("avg_confidence"),
            func.count(AgentLog.id).label("total"),
        )
        .group_by(AgentLog.agent_name)
        .all()
    )

    return [
        AgentPerformanceMetric(
            agent_name=row.agent_name,
            avg_duration_ms=round(float(row.avg_duration or 0), 1),
            avg_confidence=round(float(row.avg_confidence or 0), 2),
            total_invocations=row.total,
        )
        for row in rows
    ]


@router.get("/logs/recent")
def get_recent_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the most recent agent logs for the Agent Logs dashboard to initialize the view."""
    logs = db.query(AgentLog).order_by(AgentLog.created_at.desc()).limit(limit).all()
    # Reverse to return oldest first so they append nicely on the frontend
    logs.reverse()
    
    from app.schemas.refund import AgentLogResponse
    return [AgentLogResponse.model_validate(log) for log in logs]
