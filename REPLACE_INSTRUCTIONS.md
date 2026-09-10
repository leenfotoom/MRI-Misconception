# Replace / upgrade instructions

The challenge ZIP is a clean full-project replacement. It intentionally excludes `.env`, `.venv`, `node_modules`, `.next`, and database volumes.

## Safest replacement

1. Stop the old backend and frontend terminals.
2. Keep a private copy of the old `backend/.env`.
3. Extract the new ZIP into a new folder.
4. Copy only the private `backend/.env` into the new `backend` folder.
5. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup-windows.ps1
.\start-dev.ps1
```

Do not copy the old `.venv`, `node_modules`, or `.next` folders.

## Existing PostgreSQL volume

If the previous database was created automatically and Alembic reports that tables already exist, keep the data and run these commands from `backend`:

```powershell
.\.venv\Scripts\alembic.exe stamp 78c85b633c18
.\.venv\Scripts\alembic.exe upgrade head
```

Then restart the backend. Alembic upgrades through `0004_intervention_and_major`, adding STEM context, academic major, intervention status, post-intervention reasoning, and progress fields without deleting learner accounts or scan history.

## Required private values

Set these in `backend/.env`:

```env
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
CLOUDFLARE_MODEL=@cf/openai/gpt-oss-120b
```

Never upload or commit this file.
