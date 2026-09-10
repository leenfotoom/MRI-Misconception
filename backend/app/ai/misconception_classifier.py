from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any


CLAIM_TO_MISCONCEPTION = {
    "current_consumed": "M1",
    "proximity": "M2",
    "constant_current": "M3",
    "voltage_current_same": "M4",
    "component_uses_all": "M5",
    "sequential_arrival": "M6",
    "equal_parallel_split": "M7",
    "global_resistance": "M8",
}


def _tokens(text: str) -> Counter:
    words = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    return Counter(w for w in words if len(w) > 2)


def _cosine_counter(a: Counter, b: Counter) -> float:
    common = set(a) & set(b)
    dot = sum(a[w] * b[w] for w in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def lexical_scores(reasoning: str, misconceptions: list[dict[str, Any]]) -> dict[str, float]:
    source = _tokens(reasoning)
    out = {}
    for m in misconceptions:
        similarities = [_cosine_counter(source, _tokens(p)) for p in m["prototypes"]]
        out[m["id"]] = max(similarities, default=0.0)
    return out


def claim_scores(parsed: dict[str, Any], misconceptions: list[dict[str, Any]]) -> dict[str, float]:
    misconception_ids = [item["id"] for item in misconceptions]
    scores = {mid: 0.15 for mid in misconception_ids}
    dynamic_map = {
        item["claim"]: item["id"]
        for item in misconceptions
        if item.get("claim")
    }
    for claim in parsed.get("claims", []):
        mid = dynamic_map.get(claim) or CLAIM_TO_MISCONCEPTION.get(claim)
        if mid:
            scores[mid] = max(scores[mid], 0.95)
    return scores


def answer_scores(
    answer: str,
    misconception_ids: list[str],
    scenario: dict[str, Any] | None = None,
) -> dict[str, float]:
    # Initial scenario: two identical bulbs in series; A is drawn closer to battery.
    configured = (scenario or {}).get("answer_likelihoods", {})
    scores = {
        mid: float(configured.get(mid, {}).get(answer, 0.55))
        for mid in misconception_ids
    }
    if configured:
        return scores
    if answer == "A":
        scores.update({"M1": 0.85, "M2": 0.92, "M5": 0.75, "M6": 0.88})
    elif answer == "B":
        scores.update({"M2": 0.55, "M6": 0.45})
    elif answer == "same":
        scores.update({"M1": 0.25, "M2": 0.18, "M5": 0.25, "M6": 0.20})
    return scores


def classify(
    reasoning: str,
    answer: str,
    parsed: dict[str, Any],
    misconceptions: list[dict[str, Any]],
    scenario: dict[str, Any] | None = None,
) -> dict[str, float]:
    ids = [m["id"] for m in misconceptions]
    lex = lexical_scores(reasoning, misconceptions)
    claims = claim_scores(parsed, misconceptions)
    ans = answer_scores(answer, ids, scenario)

    # Convert lexical similarity into a usable soft likelihood and blend evidence.
    fused = {}
    for mid in ids:
        lexical_likelihood = 0.20 + 0.80 * lex[mid]
        fused[mid] = max(1e-6, lexical_likelihood * claims[mid] * ans[mid])
    total = sum(fused.values())
    return {mid: score / total for mid, score in fused.items()}
