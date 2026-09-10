from __future__ import annotations

from collections import defaultdict
from typing import Any

from .models import Scan


MAJORS: dict[str, dict[str, Any]] = {
    "computer_science": {
        "label": "Computer Science",
        "label_ar": "علوم الحاسوب",
        "domain_order": ["technology", "mathematics", "engineering", "science"],
    },
    "engineering": {
        "label": "Engineering",
        "label_ar": "الهندسة",
        "domain_order": ["engineering", "mathematics", "science", "technology"],
    },
    "mathematics": {
        "label": "Mathematics",
        "label_ar": "الرياضيات",
        "domain_order": ["mathematics", "technology", "science", "engineering"],
    },
    "natural_sciences": {
        "label": "Natural Sciences",
        "label_ar": "العلوم الطبيعية",
        "domain_order": ["science", "mathematics", "technology", "engineering"],
    },
    "information_systems": {
        "label": "Information Systems",
        "label_ar": "نظم المعلومات",
        "domain_order": ["technology", "mathematics", "engineering", "science"],
    },
    "other": {
        "label": "Other / General STEM",
        "label_ar": "تخصص آخر / STEM عام",
        "domain_order": ["science", "technology", "engineering", "mathematics"],
    },
    "undecided": {
        "label": "Not selected",
        "label_ar": "لم يُحدّد",
        "domain_order": ["science", "technology", "engineering", "mathematics"],
    },
}


def public_majors() -> list[dict[str, str]]:
    return [
        {"id": key, "label": value["label"], "label_ar": value["label_ar"]}
        for key, value in MAJORS.items()
        if key != "undecided"
    ]


def build_study_plan(*, major: str, scans: list[Scan]) -> dict[str, Any]:
    profile = MAJORS.get(major, MAJORS["other"])
    resolved = [scan for scan in scans if scan.intervention_status == "resolved"]
    persistent = [scan for scan in scans if scan.intervention_status == "persistent"]
    grouped: dict[str, list[Scan]] = defaultdict(list)
    for scan in persistent:
        grouped[scan.top_misconception_id].append(scan)

    domain_rank = {name: index for index, name in enumerate(profile["domain_order"])}
    candidates: list[dict[str, Any]] = []
    for misconception_id, attempts in grouped.items():
        latest = attempts[0]
        probability = max(float(item.post_misconception_probability or 0.0) for item in attempts)
        relevance_rank = domain_rank.get(latest.domain, len(domain_rank))
        major_relevance = max(0, 9 - relevance_rank * 3)
        severity = min(100, round(45 + probability * 35 + min(3, len(attempts)) * 8 + major_relevance))
        priority = "high" if severity >= 75 else "medium" if severity >= 55 else "low"
        candidates.append(
            {
                "id": misconception_id,
                "domain": latest.domain,
                "topic": latest.topic,
                "focus": latest.top_misconception_name,
                "priority": priority,
                "severity_score": severity,
                "persistent_attempts": len(attempts),
                "major_relevance": major_relevance,
                "why": (
                    f"MRI detected the same reasoning pattern in {len(attempts)} intervention"
                    f"{'s' if len(attempts) != 1 else ''}; latest confidence {round(probability * 100)}%. "
                    f"The {latest.domain} domain is ranked #{relevance_rank + 1} for {profile['label']}."
                ),
                "activities": [
                    f"Rebuild the core model for {latest.topic} using one worked contrast.",
                    f"Explain why the original '{latest.top_misconception_name}' rule fails.",
                    "Complete two transfer questions and justify each answer before checking it.",
                ],
                "reassessment": "Re-scan after two correct transfer answers whose reasoning uses the correct model.",
                "progress_status": "needs_reassessment",
            }
        )

    candidates.sort(
        key=lambda item: (
            -item["severity_score"],
            domain_rank.get(item["domain"], 99),
            item["topic"],
        )
    )
    for index, item in enumerate(candidates, start=1):
        item["sequence"] = index

    total = len(scans)
    resolution_rate = len(resolved) / total if total else 0.0
    return {
        "major": major,
        "major_label": profile["label"],
        "status": "action_required" if candidates else "on_track",
        "summary": (
            f"Study next: {candidates[0]['topic']} — {candidates[0]['focus']}."
            if candidates
            else "No persistent misconception is currently waiting for intervention. Continue with spaced reassessment."
        ),
        "items": candidates,
        "progress": {
            "interventions_completed": total,
            "resolved": len(resolved),
            "persistent": len(persistent),
            "resolution_rate": round(resolution_rate, 4),
        },
        "tracking_rule": "A topic moves to resolved only after a new transfer answer and its reasoning both match the expected mental model.",
    }
