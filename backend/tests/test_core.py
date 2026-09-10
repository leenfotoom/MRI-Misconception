from app.ai.misconception_classifier import classify
from app.ai.reasoning_parser import heuristic_parse
from app.learner_model.bayesian import bayes_update, uniform_prior
from app.learner_model.information_gain import expected_information_gain
from app.physics.solver import solve_parallel, solve_series
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "app" / "data"
MIS = json.loads((BASE / "misconceptions.json").read_text(encoding="utf-8"))
EXPS = json.loads((BASE / "experiments.json").read_text(encoding="utf-8"))


def test_series_equal_current_and_power():
    r = solve_series(9.0, [15.0, 15.0])
    assert round(r.current, 2) == 0.30
    assert round(r.powers[0], 6) == round(r.powers[1], 6)


def test_parallel_lower_resistance_has_more_current():
    r = solve_parallel(9.0, [15.0, 30.0])
    assert r.branch_currents[0] > r.branch_currents[1]


def test_bayes_is_normalized():
    prior = {"M1": 0.5, "M2": 0.5}
    post = bayes_update(prior, {"M1": 0.8, "M2": 0.2})
    assert abs(sum(post.values()) - 1.0) < 1e-9
    assert post["M1"] > post["M2"]


def test_information_gain_nonnegative():
    prior = uniform_prior([m["id"] for m in MIS])
    assert expected_information_gain(prior, EXPS[0]) >= 0


def test_reasoning_highlights_proximity_and_sequence():
    text = "Bulb A is brighter because electricity reaches it first and it is closer to the battery."
    parsed = heuristic_parse(text, "A")
    probs = classify(text, "A", parsed, MIS)
    assert probs["M2"] > probs["M4"]
    assert probs["M6"] > probs["M4"]
