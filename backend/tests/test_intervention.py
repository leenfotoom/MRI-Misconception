import json
from pathlib import Path
from types import SimpleNamespace

from app.intervention import PRACTICE_BY_SCENARIO, build_intervention, evaluate_intervention
from app.study_plan import build_study_plan


DATA = Path(__file__).resolve().parents[1] / "app" / "data"
SCENARIOS = {
    item["id"]: item
    for name in ("scenarios.json", "stem_scenarios.json")
    for item in json.loads((DATA / name).read_text(encoding="utf-8"))
}
MISCONCEPTIONS = {
    item["id"]: item
    for name in ("misconceptions.json", "stem_misconceptions.json")
    for item in json.loads((DATA / name).read_text(encoding="utf-8"))
}


def test_every_stem_scenario_has_targeted_transfer_practice():
    assert set(PRACTICE_BY_SCENARIO) == set(SCENARIOS)
    for scenario_id, practice in PRACTICE_BY_SCENARIO.items():
        assert practice["correct_answer"] in {item[0] for item in practice["options"]}
        assert practice["resolved_signals"]
        assert practice["persistent_signals"]
        scenario = SCENARIOS[scenario_id]
        misconception_id = scenario.get("misconception_ids", ["M1"])[0]
        payload = build_intervention(
            scenario=scenario,
            misconception=MISCONCEPTIONS[misconception_id],
            probability=0.72,
        )
        assert payload["verification_policy"]["answer_only"] is False


def test_correct_answer_without_correct_reasoning_remains_persistent():
    result = evaluate_intervention(
        scenario=SCENARIOS["T4"],
        misconception=MISCONCEPTIONS["TM7"],
        answer="B",
        reasoning="I guessed B, but 99 percent accuracy is still enough to prove the model is good.",
    )
    assert result["answer_correct"] is True
    assert result["same_misconception_detected"] is True
    assert result["status"] == "persistent"


def test_correct_transfer_reasoning_resolves_misconception():
    result = evaluate_intervention(
        scenario=SCENARIOS["T4"],
        misconception=MISCONCEPTIONS["TM7"],
        answer="B",
        reasoning="Overall accuracy hides the minority class, so I must inspect minority recall and the confusion matrix.",
    )
    assert result["answer_correct"] is True
    assert result["reasoning_matches_correct_model"] is True
    assert result["status"] == "resolved"


def test_major_plan_prioritizes_repeated_persistent_reasoning():
    scans = [
        SimpleNamespace(
            intervention_status="persistent",
            top_misconception_id="TM7",
            top_misconception_name="High accuracy proves an AI model is good",
            post_misconception_probability=0.82,
            domain="technology",
            topic="Artificial Intelligence",
        ),
        SimpleNamespace(
            intervention_status="persistent",
            top_misconception_id="TM7",
            top_misconception_name="High accuracy proves an AI model is good",
            post_misconception_probability=0.71,
            domain="technology",
            topic="Artificial Intelligence",
        ),
        SimpleNamespace(
            intervention_status="resolved",
            top_misconception_id="MM5",
            top_misconception_name="If both quantities increase, they are proportional",
            post_misconception_probability=0.15,
            domain="mathematics",
            topic="Problem Solving",
        ),
    ]
    plan = build_study_plan(major="computer_science", scans=scans)
    assert plan["major_label"] == "Computer Science"
    assert plan["items"][0]["id"] == "TM7"
    assert plan["items"][0]["priority"] == "high"
    assert plan["progress"]["resolved"] == 1
    assert plan["progress"]["persistent"] == 2
