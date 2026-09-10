from __future__ import annotations

from collections import defaultdict
from typing import Any


def _round_map(values: dict[str, float]) -> dict[str, float]:
    return {key: round(float(value), 3) for key, value in values.items()}


def _assignment_trace(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    state: dict[str, float] = {}
    for name, value in params["assignments"]:
        state[name] = state[value] if isinstance(value, str) else float(value)
    target = params["target"]
    expected = float(params["expected"])
    return "keeps_assigned_value" if state[target] == expected else "updates_with_source", {
        "x_final": state.get("x", 0),
        f"{target}_final": state[target],
    }


def _loop_range(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    values = list(range(int(params["start"]), int(params["stop"]), int(params.get("step", 1))))
    expected = int(params["expected_count"])
    return "stop_excluded" if len(values) == expected else "stop_included", {
        "first_value": values[0],
        "last_value": values[-1],
        "iterations": len(values),
    }


def _sql_precedence(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    rows = params["rows"]
    ungrouped = [row for row in rows if (row["active"] and row["premium"]) or row["trial"]]
    grouped = [row for row in rows if row["active"] and (row["premium"] or row["trial"])]
    outcome = "and_before_or" if len(ungrouped) != len(grouped) else "same_result"
    return outcome, {"ungrouped_rows": len(ungrouped), "grouped_rows": len(grouped)}


def _classification_metrics(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    tp, tn = float(params["tp"]), float(params["tn"])
    fp, fn = float(params["fp"]), float(params["fn"])
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    recall = tp / (tp + fn) if tp + fn else 0.0
    outcome = "high_accuracy_low_recall" if accuracy >= 0.9 and recall < 0.5 else "accuracy_sufficient"
    return outcome, {"accuracy_percent": accuracy * 100, "minority_recall_percent": recall * 100}


def _beam_reactions(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    load, length, distance = float(params["load"]), float(params["length"]), float(params["distance_from_left"])
    right = load * distance / length
    left = load - right
    if abs(left - right) < 1e-9:
        outcome = "same"
    else:
        outcome = "left_higher" if left > right else "right_higher"
    return outcome, {"left_reaction": left, "right_reaction": right}


def _axial_stress(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    load = float(params["load"])
    thin = load / float(params["thin_area"])
    thick = load / float(params["thick_area"])
    return "thin_higher" if thin > thick else "thick_higher", {"thin_stress": thin, "thick_stress": thick}


def _design_constraints(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    budget = float(params["budget"])
    minimum = float(params["minimum_strength"])
    candidates = params["candidates"]
    feasible = [item for item in candidates if item["cost"] <= budget and item["strength"] >= minimum]
    best = max(feasible, key=lambda item: item["score"])
    return best["outcome"], {"feasible_designs": len(feasible), "winning_score": best["score"]}


def _multiobjective(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    weights = params["weights"]
    scored = []
    for item in params["candidates"]:
        score = sum(float(item[key]) * float(weight) for key, weight in weights.items())
        scored.append((score, item))
    score, best = max(scored, key=lambda pair: pair[0])
    return best["outcome"], {"balanced_score": score, "alternatives_tested": len(scored)}


def _linear_equation(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    a, b, c = float(params["a"]), float(params["b"]), float(params["c"])
    solution = c / a - b
    check = a * (solution + b)
    return "solution_verified", {"x": solution, "left_side": check, "right_side": c}


def _mapping_function(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    outputs: dict[float, set[float]] = defaultdict(set)
    for x, y in params["pairs"]:
        outputs[float(x)].add(float(y))
    conflicts = sum(1 for values in outputs.values() if len(values) > 1)
    return "not_a_function" if conflicts else "is_a_function", {"inputs": len(outputs), "conflicting_inputs": conflicts}


def _proportional_table(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    ratios = [float(y) / float(x) for x, y in params["pairs"]]
    spread = max(ratios) - min(ratios)
    return "not_proportional" if spread > 1e-9 else "proportional", {
        "first_ratio": ratios[0],
        "last_ratio": ratios[-1],
        "ratio_spread": spread,
    }


def _converse_counterexample(params: dict[str, Any]) -> tuple[str, dict[str, float]]:
    value = int(params["counterexample"])
    is_even = value % 2 == 0
    divisible_by_four = value % 4 == 0
    outcome = "converse_false" if is_even and not divisible_by_four else "converse_true"
    return outcome, {"counterexample": value, "is_even": int(is_even), "divisible_by_four": int(divisible_by_four)}


SOLVERS = {
    "assignment_trace": _assignment_trace,
    "loop_range": _loop_range,
    "sql_precedence": _sql_precedence,
    "classification_metrics": _classification_metrics,
    "beam_reactions": _beam_reactions,
    "axial_stress": _axial_stress,
    "design_constraints": _design_constraints,
    "multiobjective": _multiobjective,
    "linear_equation": _linear_equation,
    "mapping_function": _mapping_function,
    "proportional_table": _proportional_table,
    "converse_counterexample": _converse_counterexample,
}


def solve_experiment(experiment: dict[str, Any]) -> dict[str, Any]:
    engine = experiment["engine"]
    solver = SOLVERS.get(engine["type"])
    if solver is None:
        raise ValueError(f"Unsupported evidence engine: {engine['type']}")
    outcome, measurements = solver(engine.get("params", {}))
    if outcome not in experiment["options"]:
        raise ValueError(f"Engine produced an undeclared outcome: {outcome}")
    return {
        "experiment_id": experiment["id"],
        "actual_outcome": outcome,
        "measurements": _round_map(measurements),
        "explanation": engine["explanation"],
        "engine": engine["type"],
    }
