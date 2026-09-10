from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import Scan, utcnow


def create_scan(
    db: Session,
    *,
    user_id: str,
    scenario_id: str,
    scenario_title: str,
    domain: str = "science",
    topic: str = "Electricity",
    answer: str,
    reasoning: str,
    parser: str,
    top_misconception_id: str,
    top_misconception_name: str,
    before_probability: float,
    experiment_id: str,
    experiment_name: str,
    information_gain: float,
    posterior_before: dict[str, float],
) -> str:
    scan = Scan(
        user_id=user_id,
        scenario_id=scenario_id,
        scenario_title=scenario_title,
        domain=domain,
        topic=topic,
        answer=answer,
        reasoning=reasoning,
        parser=parser,
        top_misconception_id=top_misconception_id,
        top_misconception_name=top_misconception_name,
        before_probability=float(before_probability),
        experiment_id=experiment_id,
        experiment_name=experiment_name,
        information_gain=float(information_gain),
        posterior_before=posterior_before,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan.id


def complete_scan(db: Session, *, scan_id: str, user_id: str, actual_outcome: str, posterior_after: dict[str, float]) -> None:
    scan = db.scalar(select(Scan).where(Scan.id == scan_id, Scan.user_id == user_id))
    if scan is None:
        return
    scan.completed_at = utcnow()
    scan.actual_outcome = actual_outcome
    scan.after_probability = float(posterior_after.get(scan.top_misconception_id, 0.0))
    scan.posterior_after = posterior_after
    db.commit()


def get_scan(db: Session, *, scan_id: str, user_id: str) -> Scan | None:
    return db.scalar(select(Scan).where(Scan.id == scan_id, Scan.user_id == user_id))


def start_scan_intervention(db: Session, *, scan: Scan) -> None:
    if scan.intervention_started_at is None:
        scan.intervention_started_at = utcnow()
        db.commit()


def complete_scan_intervention(
    db: Session,
    *,
    scan: Scan,
    status: str,
    answer: str,
    reasoning: str,
    post_probability: float,
) -> None:
    scan.intervention_completed_at = utcnow()
    scan.intervention_status = status
    scan.intervention_answer = answer
    scan.intervention_reasoning = reasoning
    scan.post_misconception_probability = float(post_probability)
    db.commit()


def _to_record(scan: Scan) -> dict[str, Any]:
    return {
        "id": scan.id,
        "createdAt": scan.created_at.isoformat(),
        "completedAt": scan.completed_at.isoformat() if scan.completed_at else None,
        "scenarioId": scan.scenario_id,
        "scenarioTitle": scan.scenario_title,
        "domain": scan.domain,
        "topic": scan.topic,
        "misconceptionId": scan.top_misconception_id,
        "misconception": scan.top_misconception_name,
        "before": scan.before_probability,
        "after": scan.after_probability,
        "experiment": scan.experiment_name,
        "informationGain": scan.information_gain,
        "parser": scan.parser,
        "completed": scan.completed_at is not None,
        "interventionStatus": scan.intervention_status,
        "interventionCompletedAt": scan.intervention_completed_at.isoformat() if scan.intervention_completed_at else None,
        "postMisconceptionProbability": scan.post_misconception_probability,
    }


def list_history(db: Session, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
    safe_limit = max(1, min(int(limit), 200))
    rows = db.scalars(
        select(Scan)
        .where(Scan.user_id == user_id, Scan.completed_at.is_not(None))
        .order_by(Scan.created_at.desc())
        .limit(safe_limit)
    ).all()
    return [_to_record(row) for row in rows]


def learner_insights(db: Session, user_id: str) -> dict[str, Any]:
    history = list_history(db, user_id, 200)
    if not history:
        return {
            "totalScans": 0,
            "averageShift": 0.0,
            "largestShift": 0.0,
            "aggregated": [],
            "scenarioCoverage": [],
            "domainCoverage": [],
            "interventionProgress": {"completed": 0, "resolved": 0, "persistent": 0, "resolutionRate": 0.0},
        }

    shifts = [abs(item["before"] - (item["after"] or 0.0)) for item in history]
    grouped: dict[str, dict[str, Any]] = {}
    scenario_counts: dict[str, dict[str, Any]] = {}
    domain_counts: dict[str, int] = {}

    for item in history:
        mid = item["misconceptionId"]
        bucket = grouped.setdefault(mid, {"id": mid, "name": item["misconception"], "total": 0.0, "count": 0})
        bucket["total"] += float(item["before"])
        bucket["count"] += 1

        sid = item["scenarioId"]
        sc = scenario_counts.setdefault(sid, {"id": sid, "title": item["scenarioTitle"], "count": 0})
        sc["count"] += 1

        domain = item.get("domain", "science")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    aggregated = [
        {
            "id": value["id"],
            "name": value["name"],
            "probability": value["total"] / value["count"],
            "observations": value["count"],
        }
        for value in grouped.values()
    ]
    aggregated.sort(key=lambda item: item["probability"], reverse=True)
    coverage = sorted(scenario_counts.values(), key=lambda item: item["count"], reverse=True)
    domain_coverage = [
        {"domain": domain, "count": count}
        for domain, count in sorted(domain_counts.items(), key=lambda item: item[1], reverse=True)
    ]
    intervention_items = [item for item in history if item.get("interventionStatus") in {"resolved", "persistent"}]
    resolved_count = sum(1 for item in intervention_items if item["interventionStatus"] == "resolved")
    persistent_count = sum(1 for item in intervention_items if item["interventionStatus"] == "persistent")

    return {
        "totalScans": len(history),
        "averageShift": sum(shifts) / len(shifts),
        "largestShift": max(shifts),
        "aggregated": aggregated[:8],
        "scenarioCoverage": coverage,
        "domainCoverage": domain_coverage,
        "interventionProgress": {
            "completed": len(intervention_items),
            "resolved": resolved_count,
            "persistent": persistent_count,
            "resolutionRate": resolved_count / len(intervention_items) if intervention_items else 0.0,
        },
    }


def clear_history(db: Session, user_id: str) -> int:
    result = db.execute(delete(Scan).where(Scan.user_id == user_id))
    db.commit()
    return int(result.rowcount or 0)


def intervention_scans(db: Session, user_id: str) -> list[Scan]:
    return list(
        db.scalars(
            select(Scan)
            .where(Scan.user_id == user_id, Scan.intervention_status.is_not(None))
            .order_by(Scan.intervention_completed_at.desc())
        ).all()
    )
