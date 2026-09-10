from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .ai.misconception_classifier import classify
from .ai.reasoning_parser import parse_reasoning
from .database import Base, engine, get_db
from .learner_model.bayesian import bayes_update, uniform_prior
from .learner_model.information_gain import rank_experiments
from .intervention import build_intervention, evaluate_intervention
from .models import Domain
from .physics.solver import solve_parallel, solve_series
from .evidence.solver import solve_experiment
from .routes.auth import router as auth_router
from .routes.profile import router as profile_router
from .security import AuthContext, get_auth_context, require_csrf
from .storage import (
    clear_history,
    complete_scan,
    create_scan,
    complete_scan_intervention,
    get_scan,
    intervention_scans,
    learner_insights,
    list_history,
    start_scan_intervention,
)
from .study_plan import build_study_plan, public_majors


BASE = Path(__file__).resolve().parent

MISCONCEPTIONS = json.loads(
    (BASE / "data" / "misconceptions.json").read_text(encoding="utf-8")
)

MISCONCEPTIONS += json.loads(
    (BASE / "data" / "stem_misconceptions.json").read_text(encoding="utf-8")
)

EXPERIMENTS = json.loads(
    (BASE / "data" / "experiments.json").read_text(encoding="utf-8")
)

EXPERIMENTS += json.loads(
    (BASE / "data" / "stem_experiments.json").read_text(encoding="utf-8")
)

SCENARIOS = json.loads(
    (BASE / "data" / "scenarios.json").read_text(encoding="utf-8")
)

SCENARIOS += json.loads(
    (BASE / "data" / "stem_scenarios.json").read_text(encoding="utf-8")
)

SCIENCE_SCENARIO_MODELS = {
    "S1": ["M1", "M2", "M5", "M6"],
    "S2": ["M3", "M4", "M8"],
    "S3": ["M4", "M7", "M8"],
    "S4": ["M1", "M4", "M5"],
}

for item in SCENARIOS:
    item.setdefault("domain", "science")
    item.setdefault("topic", "Electricity")
    if item["id"] in SCIENCE_SCENARIO_MODELS:
        item.setdefault("misconception_ids", SCIENCE_SCENARIO_MODELS[item["id"]])


MISCONCEPTION_BY_ID = {
    m["id"]: m for m in MISCONCEPTIONS
}

EXPERIMENT_BY_ID = {
    e["id"]: e for e in EXPERIMENTS
}

SCENARIO_BY_ID = {
    s["id"]: s for s in SCENARIOS
}



def seed_domains(db: Session):

    domains = [
        {
            "name": "Physics",
            "description": "Physical systems, energy, motion and scientific reasoning.",
            "icon": "⚡",
        },
        {
            "name": "Mathematics",
            "description": "Mathematical thinking, logic and problem solving.",
            "icon": "📐",
        },
        {
            "name": "Engineering",
            "description": "Applied engineering concepts and design thinking.",
            "icon": "⚙️",
        },
        {
            "name": "Technology",
            "description": "Programming, artificial intelligence and digital systems.",
            "icon": "💻",
        },
    ]

    existing = {item.name for item in db.query(Domain).all()}

    for item in domains:
        if item["name"] not in existing:
            db.add(Domain(**item))

    db.commit()



if os.getenv("AUTO_CREATE_SCHEMA", "1") == "1":

    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        seed_domains(db)



app = FastAPI(
    title="Misconception MRI API",
    version="1.0.0",
    description="Closed-loop STEM learning platform with misconception diagnosis, targeted intervention, reasoning-based verification, and major-aware study planning.",
)



origins = [
    item.strip()
    for item in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if item.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(auth_router)
app.include_router(profile_router)



class DiagnoseRequest(BaseModel):

    answer: str = Field(
        pattern="^(A|B|same)$"
    )

    reasoning: str = Field(
        min_length=2,
        max_length=1200
    )

    prior: dict[str, float] | None = None

    scenario_id: str = "S1"



class UpdateRequest(BaseModel):

    experiment_id: str

    outcome: str

    prior: dict[str, float]

    scan_id: str | None = None


class InterventionStartRequest(BaseModel):
    scan_id: str


class InterventionVerifyRequest(BaseModel):
    scan_id: str
    answer: str = Field(pattern="^(A|B|same)$")
    reasoning: str = Field(min_length=5, max_length=1200)



def public_scenario(
    scenario: dict[str, Any]
):

    return {
        "id": scenario["id"],
        "code": scenario["code"],
        "title": scenario["title"],
        "title_ar": scenario["title_ar"],
        "question": scenario["question"],
        "question_ar": scenario["question_ar"],
        "options": scenario["options"],
        "sample_reasoning": scenario["sample_reasoning"],
        "sample_reasoning_ar": scenario["sample_reasoning_ar"],
        "circuit": scenario["circuit"],
        "concepts": scenario["concepts"],
        "domain": scenario.get("domain", "science"),
        "topic": scenario.get("topic", "Electricity"),
    }



@app.get("/health")
def health():

    return {
        "status": "ok",
        "project": "Misconception MRI",
        "version": "1.0.0"
    }



@app.get("/api/status")
def platform_status():

    return {

        "status": "operational",

        "version": "1.0.0",

        "persistence": "postgresql",

        "identity": "account-based",

        "ai_provider": "cloudflare-workers-ai",

        "ai_model": os.getenv(
            "CLOUDFLARE_MODEL",
            "@cf/openai/gpt-oss-120b"
        ),

        "physics_engine": "deterministic",

        "evidence_engines": [
            "physics",
            "code-trace",
            "engineering",
            "mathematics",
        ],

        "scenario_count": len(SCENARIOS),

        "misconception_count": len(MISCONCEPTIONS),

        "learning_loop": [
            "diagnose",
            "intervene",
            "practice",
            "reasoning-verification",
            "major-aware-plan",
        ],

    }



@app.get("/api/domains")
def domains(
    db: Session = Depends(get_db)
):

    items = db.query(Domain).filter(
        Domain.name.in_(["Physics", "Mathematics", "Engineering", "Technology"])
    ).all()

    return [

        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "icon": item.icon,
        }

        for item in items

    ]



@app.get("/api/scenarios")
def scenarios(
    domain: str | None = Query(default=None)
):

    return [
        public_scenario(item)
        for item in SCENARIOS
        if domain is None or item.get("domain", "science") == domain.lower()
    ]



@app.get("/api/scenario")
def scenario_legacy():

    return public_scenario(
        SCENARIOS[0]
    )



@app.get("/api/scenarios/{scenario_id}")
def scenario_by_id(
    scenario_id: str
):

    item = SCENARIO_BY_ID.get(
        scenario_id
    )

    if item is None:

        raise HTTPException(
            status_code=404,
            detail="Unknown scenario"
        )

    return public_scenario(item)



@app.post("/api/diagnose")
def diagnose(
    req: DiagnoseRequest,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
):

    scenario = SCENARIO_BY_ID.get(
        req.scenario_id
    )

    if scenario is None:

        raise HTTPException(
            status_code=404,
            detail="Unknown scenario"
        )


    allowed_misconceptions = set(scenario.get("misconception_ids", []))

    scenario_misconceptions = [
        m for m in MISCONCEPTIONS
        if not allowed_misconceptions or m["id"] in allowed_misconceptions
    ]

    ids = [m["id"] for m in scenario_misconceptions]


    prior = req.prior or uniform_prior(ids)


    parsed = parse_reasoning(
        req.reasoning,
        req.answer,
        scenario_misconceptions,
    )


    evidence = classify(
        req.reasoning,
        req.answer,
        parsed,
        scenario_misconceptions,
        scenario,
    )


    posterior = bayes_update(
        prior,
        evidence
    )


    allowed = set(
        scenario.get(
            "experiment_ids",
            []
        )
    )


    candidate_experiments = [
        e for e in EXPERIMENTS
        if not allowed or e["id"] in allowed
    ]


    ranked = rank_experiments(
        posterior,
        candidate_experiments
    )


    if not ranked:

        raise HTTPException(
            status_code=500,
            detail="No diagnostic experiment available for this scenario."
        )


    best = ranked[0]


    top = sorted(
        posterior.items(),
        key=lambda kv: kv[1],
        reverse=True
    )


    top_id, top_probability = top[0]



    scan_id = create_scan(

        db,

        user_id=auth.user.id,

        scenario_id=scenario["id"],

        scenario_title=scenario["title"],

        domain=scenario.get("domain", "science"),

        topic=scenario.get("topic", "Electricity"),

        answer=req.answer,

        reasoning=req.reasoning,

        parser=parsed.get(
            "parser",
            "unknown"
        ),

        top_misconception_id=top_id,

        top_misconception_name=MISCONCEPTION_BY_ID[top_id]["short"],

        before_probability=top_probability,

        experiment_id=best["id"],

        experiment_name=best["name"],

        information_gain=best["information_gain"],

        posterior_before=posterior,

    )


    return {

        "scan_id": scan_id,

        "scenario_id": scenario["id"],

        "parsed_reasoning": parsed,

        "posterior": posterior,

        "domain": scenario.get("domain", "science"),

        "topic": scenario.get("topic", "Electricity"),

        "top_hypotheses": [
            {
                "id": mid,
                "name": MISCONCEPTION_BY_ID[mid]["short"],
                "probability": probability,
            }
            for mid, probability in top[:4]
        ],

        "next_experiment": {
            "id": best["id"],
            "name": best["name"],
            "description": best["description"],
            "prompt": best["prompt"],
            "options": best["options"],
            "information_gain": best["information_gain"],
        },

        "experiment_ranking": [
            {
                "id": item["id"],
                "name": item["name"],
                "information_gain": item["information_gain"],
            }
            for item in ranked
        ],

    }



@app.get("/api/history")
def history(
    limit: int = Query(default=50),
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):

    return {
        "items": list_history(
            db,
            auth.user.id,
            limit
        )
    }



@app.get("/api/insights")
def insights(
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):

    return learner_insights(
        db,
        auth.user.id
    )


@app.get("/api/majors")
def majors():
    return public_majors()


@app.post("/api/interventions/start")
def start_intervention(
    req: InterventionStartRequest,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    scan = get_scan(db, scan_id=req.scan_id, user_id=auth.user.id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Unknown scan")
    if scan.completed_at is None:
        raise HTTPException(status_code=409, detail="Complete the diagnostic experiment before intervention.")
    scenario = SCENARIO_BY_ID.get(scan.scenario_id)
    misconception = MISCONCEPTION_BY_ID.get(scan.top_misconception_id)
    if scenario is None or misconception is None:
        raise HTTPException(status_code=409, detail="The diagnostic catalog changed; start a new scan.")
    start_scan_intervention(db, scan=scan)
    return {
        "scan_id": scan.id,
        **build_intervention(
            scenario=scenario,
            misconception=misconception,
            probability=float(scan.after_probability if scan.after_probability is not None else scan.before_probability),
        ),
    }


@app.post("/api/interventions/verify")
def verify_intervention(
    req: InterventionVerifyRequest,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    scan = get_scan(db, scan_id=req.scan_id, user_id=auth.user.id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Unknown scan")
    if scan.intervention_started_at is None:
        raise HTTPException(status_code=409, detail="Start the intervention before verification.")
    scenario = SCENARIO_BY_ID.get(scan.scenario_id)
    misconception = MISCONCEPTION_BY_ID.get(scan.top_misconception_id)
    if scenario is None or misconception is None:
        raise HTTPException(status_code=409, detail="The diagnostic catalog changed; start a new scan.")

    result = evaluate_intervention(
        scenario=scenario,
        misconception=misconception,
        answer=req.answer,
        reasoning=req.reasoning,
    )
    complete_scan_intervention(
        db,
        scan=scan,
        status=result["status"],
        answer=req.answer,
        reasoning=req.reasoning,
        post_probability=result["post_misconception_probability"],
    )
    return {
        "scan_id": scan.id,
        "misconception_id": scan.top_misconception_id,
        "major": auth.user.academic_major,
        "study_plan_available": result["status"] == "persistent" and auth.user.academic_major != "undecided",
        **result,
    }


@app.get("/api/study-plan")
def study_plan(
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    if auth.user.academic_major == "undecided":
        raise HTTPException(status_code=409, detail="Select an academic major before generating a study plan.")
    return build_study_plan(
        major=auth.user.academic_major,
        scans=intervention_scans(db, auth.user.id),
    )


@app.post("/api/update")
def update_model(
    req: UpdateRequest,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    experiment = EXPERIMENT_BY_ID.get(req.experiment_id)

    if experiment is None:
        raise HTTPException(status_code=404, detail="Unknown experiment")

    if req.outcome not in experiment["options"]:
        raise HTTPException(status_code=400, detail="Outcome not valid for this experiment")

    likelihood = {
        mid: experiment["likelihoods"].get(mid, {}).get(req.outcome, 1e-6)
        for mid in req.prior
    }

    posterior = bayes_update(req.prior, likelihood)

    if req.scan_id:
        complete_scan(
            db,
            scan_id=req.scan_id,
            user_id=auth.user.id,
            actual_outcome=req.outcome,
            posterior_after=posterior,
        )

    return {"posterior": posterior}


@app.delete("/api/history")
def delete_history(
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    return {"deleted": clear_history(db, auth.user.id)}


@app.get("/api/simulate/{experiment_id}")
def simulate(experiment_id: str):
    experiment = EXPERIMENT_BY_ID.get(experiment_id)

    if experiment is None:
        raise HTTPException(status_code=404, detail="Unknown experiment")

    if experiment.get("engine"):
        return solve_experiment(experiment)

    if experiment_id in {"E1", "E2"}:
        result = solve_series(9.0, [15.0, 15.0])
        return {
            "experiment_id": experiment_id,
            "actual_outcome": "same",
            "measurements": {
                "current_A": round(result.current, 3),
                "current_B": round(result.current, 3),
                "power_A": round(result.powers[0], 3),
                "power_B": round(result.powers[1], 3),
            },
            "explanation": "The same current flows through every component in this ideal series loop, and identical bulbs dissipate equal power.",
        }

    if experiment_id == "E3":
        one = solve_series(9.0, [15.0])
        two = solve_series(9.0, [15.0, 15.0])
        return {
            "experiment_id": experiment_id,
            "actual_outcome": "decreases",
            "measurements": {
                "current_before": round(one.current, 3),
                "current_after": round(two.current, 3),
            },
            "explanation": "With the same battery voltage, doubling series resistance halves the total current in this ideal circuit.",
        }

    result = solve_parallel(9.0, [15.0, 30.0])
    return {
        "experiment_id": experiment_id,
        "actual_outcome": "lower_resistance_more",
        "measurements": {
            "branch_15_ohm": round(result.branch_currents[0], 3),
            "branch_30_ohm": round(result.branch_currents[1], 3),
        },
        "explanation": "Parallel branches share the same voltage, so the lower-resistance branch carries more current.",
    }
