import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import User
from app.storage import complete_scan, create_scan, learner_insights, list_history


def test_scenario_catalog_has_multiple_real_scenarios():
    path = Path(__file__).resolve().parents[1] / "app" / "data" / "scenarios.json"
    scenarios = json.loads(path.read_text(encoding="utf-8"))
    assert len(scenarios) >= 4
    assert all(item["experiment_ids"] for item in scenarios)
    assert {item["circuit"]["type"] for item in scenarios} >= {
        "series_bulbs",
        "resistance_change",
        "parallel_branches",
        "ammeter_series",
    }


def test_account_scoped_history_round_trip():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user = User(full_name="Learner", email="learner@example.com", password_hash="x", is_email_verified=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        scan_id = create_scan(
            db,
            user_id=user.id,
            scenario_id="S1",
            scenario_title="Identical bulbs in series",
            answer="A",
            reasoning="Closer to battery gets more electricity",
            parser="heuristic_fallback",
            top_misconception_id="M2",
            top_misconception_name="Closer to battery = more power",
            before_probability=0.64,
            experiment_id="E1",
            experiment_name="Swap Identical Bulbs",
            information_gain=0.68,
            posterior_before={"M2": 0.64, "M1": 0.36},
        )
        complete_scan(db, scan_id=scan_id, user_id=user.id, actual_outcome="same", posterior_after={"M2": 0.16, "M1": 0.84})
        history = list_history(db, user.id)
        assert len(history) == 1
        assert history[0]["after"] == 0.16
        insights = learner_insights(db, user.id)
        assert insights["totalScans"] == 1
        assert round(insights["averageShift"], 2) == 0.48
