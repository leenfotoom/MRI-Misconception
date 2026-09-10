# Misconception MRI v0.7 — Product Core Upgrade

Replace the matching files in your existing project with this patch.

## What changes

- 4 real diagnostic scenarios instead of one fixed circuit
- different circuit environments for series bulbs, resistance change, parallel branches, and dual-ammeters
- persistent learner history in the backend
- real Insights data from the backend instead of browser-only mock/local history
- anonymous learner ID persisted in the browser and linked to server-side scans
- scenario coverage analytics
- clear-history privacy action
- platform status API
- configurable `ALLOWED_ORIGINS`
- isolated SQLite storage layer ready to be replaced by PostgreSQL later
- README rewritten as a deployable product, not a competition demo

## Your secrets are safe

This patch does **not** include `.env` and will not overwrite your Cloudflare credentials.

## After replace

Backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm run dev
```

No new Python or npm package is required for v0.7.

The SQLite database is created automatically at `backend/data/misconception_mri.db` unless `MRI_DATABASE_PATH` is set.
