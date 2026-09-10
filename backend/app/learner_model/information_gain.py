from __future__ import annotations

import math
from typing import Any, Mapping

from .bayesian import bayes_update, normalize


def entropy(distribution: Mapping[str, float]) -> float:
    h = 0.0
    for p in distribution.values():
        if p > 0:
            h -= p * math.log2(p)
    return h


def expected_information_gain(prior: Mapping[str, float], experiment: Mapping[str, Any]) -> float:
    prior = normalize(prior)
    base = entropy(prior)
    outcomes = experiment["options"]
    likelihoods = experiment["likelihoods"]

    expected_posterior_entropy = 0.0
    for outcome in outcomes:
        # P(outcome) = sum_m P(outcome|m) P(m)
        p_outcome = sum(
            prior[mid] * float(likelihoods[mid].get(outcome, 0.0))
            for mid in prior
        )
        if p_outcome <= 0:
            continue
        outcome_likelihood = {
            mid: float(likelihoods[mid].get(outcome, 1e-6))
            for mid in prior
        }
        posterior = bayes_update(prior, outcome_likelihood)
        expected_posterior_entropy += p_outcome * entropy(posterior)

    return max(0.0, base - expected_posterior_entropy)


def rank_experiments(prior: Mapping[str, float], experiments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = []
    for exp in experiments:
        ig = expected_information_gain(prior, exp)
        ranked.append({**exp, "information_gain": ig})
    ranked.sort(key=lambda e: e["information_gain"], reverse=True)
    return ranked
