# Misconception MRI — Closed-Loop STEM Learning

Misconception MRI identifies the hidden mental model behind a learner's answer, delivers a targeted intervention, verifies whether the learner's reasoning changed, and converts persistent misconceptions into a study plan based on the learner's academic major.

## Why it is different

Most educational AI explains the right answer after a mistake. Misconception MRI closes the learning loop:

**Assess → Diagnose → Challenge → Explain → Targeted Learning → Transfer Practice → Reasoning Verification → Resolved / Persistent → Major-Aware Study Plan**

A correct final answer is not automatically marked Resolved. The transfer answer, correct-model reasoning, and absence of the original misconception pattern are evaluated independently.

The LLM never decides what is true:

1. **GPT-OSS 120B** extracts constrained reasoning signals from English or Arabic explanations.
2. **Bayesian inference** maintains probabilities across competing misconceptions.
3. **Information gain** selects the most discriminating next experiment.
4. **Deterministic evidence engines** compute the observable result.
5. **Targeted intervention** explains the detected gap and teaches the replacement mental model.
6. **Reasoning verification** evaluates a new transfer answer and explanation.
7. **Major-aware planning** prioritizes only misconceptions that remain Persistent.

## STEM coverage

| Domain | Diagnostic environments | Evidence engine |
| --- | ---: | --- |
| Science / Electricity | 4 | Series and parallel circuit solvers |
| Technology | 4 | Code trace, loop bounds, SQL precedence, AI metrics |
| Engineering | 4 | Equilibrium, stress, constraints, multi-objective scoring |
| Mathematics | 4 | Equations, functions, ratios, logic counterexamples |

The challenge build includes **16 scenarios, 32 misconception models, 16 diagnostic experiments, and targeted transfer practice for every scenario**.

## Intervention and planning API

- `POST /api/interventions/start` returns the detected pattern, simple explanation, correct model, micro-lesson, and transfer question.
- `POST /api/interventions/verify` stores a reasoning-based `resolved` or `persistent` result.
- `GET /api/majors` returns supported academic-major profiles.
- `GET /api/study-plan` ranks persistent misconceptions by severity, recurrence, and major relevance.
- `GET /api/insights` includes intervention completion and resolution progress.

## Stack

- Next.js 16.3.3 + React 19.2 + TypeScript
- FastAPI + Pydantic
- SQLAlchemy + PostgreSQL + Alembic
- Cloudflare Workers AI / GPT-OSS 120B with a transparent heuristic fallback
- Argon2 passwords, HttpOnly sessions, CSRF protection, email verification, and account-scoped scan history

## One-command Windows setup

Requirements: Python 3.11+, Node.js 20+, Docker Desktop.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup-windows.ps1
.\start-dev.ps1
```

Open `http://localhost:3000`. In local console-email mode, registration exposes a verification link without requiring a mail provider.

Add Cloudflare credentials to `backend/.env` to activate GPT-OSS. Without credentials the product stays functional through the explainable heuristic parser.

## Manual setup

```powershell
docker compose up -d postgres

cd backend
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\alembic upgrade head
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
Copy-Item .env.local.example .env.local
npm ci
npm run dev
```

## Verification

```powershell
.\run-tests.ps1
```

The backend suite checks Bayesian inference, security utilities, persistence, every deterministic TEM engine, bilingual diagnosis signals, all 16 transfer-practice definitions, reasoning-based Resolved/Persistent behavior, and major-aware prioritization. The frontend command produces a typed optimized production build.

## Production

Use HTTPS, managed PostgreSQL, `AUTO_CREATE_SCHEMA=0`, exact allowed origins, secure cookies, a verified email provider, and secrets supplied by the hosting platform. Never commit `backend/.env`.

See `PITCH.md` for the Devpost story and the exact two-minute video script. See `REPLACE_INSTRUCTIONS.md` when upgrading an earlier challenge folder.
