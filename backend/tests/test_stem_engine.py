import json
from pathlib import Path

from app.ai.misconception_classifier import classify
from app.ai.reasoning_parser import heuristic_parse
from app.evidence.solver import solve_experiment


DATA = Path(__file__).resolve().parents[1] / "app" / "data"
MISCONCEPTIONS = json.loads((DATA / "stem_misconceptions.json").read_text(encoding="utf-8"))
SCENARIOS = json.loads((DATA / "stem_scenarios.json").read_text(encoding="utf-8"))
EXPERIMENTS = json.loads((DATA / "stem_experiments.json").read_text(encoding="utf-8"))


def test_tem_catalog_has_four_scenarios_per_domain():
    for domain in {"technology", "engineering", "mathematics"}:
        assert len([item for item in SCENARIOS if item["domain"] == domain]) == 4


def test_every_stem_experiment_has_a_deterministic_result():
    for experiment in EXPERIMENTS:
        result = solve_experiment(experiment)
        assert result["actual_outcome"] in experiment["options"]
        assert result["measurements"]


def test_technology_reasoning_identifies_accuracy_only_model():
    scenario = next(item for item in SCENARIOS if item["id"] == "T4")
    allowed = [item for item in MISCONCEPTIONS if item["id"] in scenario["misconception_ids"]]
    reasoning = "99 percent means good, accuracy is enough even if the minority class is missed"
    parsed = heuristic_parse(reasoning, "B", allowed)
    posterior = classify(reasoning, "B", parsed, allowed, scenario)
    assert posterior["TM7"] > 0.5


def test_arabic_reasoning_can_trigger_a_stem_claim():
    scenario = next(item for item in SCENARIOS if item["id"] == "MATH3")
    allowed = [item for item in MISCONCEPTIONS if item["id"] in scenario["misconception_ids"]]
    parsed = heuristic_parse("العلاقة تناسبية لأن القيمتين يزيدان معًا", "B", allowed)
    assert "increase_means_proportional" in parsed["claims"]
