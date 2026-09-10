from __future__ import annotations

from typing import Mapping


def normalize(weights: Mapping[str, float]) -> dict[str, float]:
    safe = {k: max(float(v), 1e-12) for k, v in weights.items()}
    total = sum(safe.values())
    return {k: v / total for k, v in safe.items()}


def uniform_prior(ids: list[str]) -> dict[str, float]:
    if not ids:
        return {}
    p = 1.0 / len(ids)
    return {mid: p for mid in ids}


def bayes_update(prior: Mapping[str, float], likelihood: Mapping[str, float]) -> dict[str, float]:
    """Posterior proportional to prior * likelihood."""
    weighted = {
        mid: max(prior.get(mid, 1e-12), 1e-12) * max(likelihood.get(mid, 1e-6), 1e-6)
        for mid in prior
    }
    return normalize(weighted)


def blend_evidence(*evidence_maps: Mapping[str, float], floor: float = 0.05) -> dict[str, float]:
    """Geometric-style fusion of independent soft evidence maps.

    Values are not probabilities themselves; they act as soft likelihoods.
    """
    if not evidence_maps:
        return {}
    ids = set().union(*(m.keys() for m in evidence_maps))
    fused: dict[str, float] = {}
    for mid in ids:
        score = 1.0
        for evidence in evidence_maps:
            score *= max(float(evidence.get(mid, floor)), floor)
        fused[mid] = score
    return normalize(fused)
