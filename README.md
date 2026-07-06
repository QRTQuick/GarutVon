# GarutVON

GarutVON is a Universal File Productivity Platform for desktop file workflows, cloud APIs, developer automation, dashboards and update delivery.

## Stack

- Flask for website pages, authentication, dashboards, downloads, support, admin and API key management
- FastAPI for REST endpoints under `/api`
- PostgreSQL with SQLAlchemy and Alembic
- Plain HTML5, CSS3 and vanilla JavaScript
- Vercel-ready Python entrypoint at `garutvon/wsgi.py`

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
$env:DATABASE_URL="sqlite:///garutvon_dev.db"
flask --app garutvon run
```

Open `http://127.0.0.1:5000`.

## API examples

```powershell
curl http://127.0.0.1:5000/api/health
curl http://127.0.0.1:5000/api/version
curl -X POST http://127.0.0.1:5000/api/summarize -H "Content-Type: application/json" -d "{\"text\":\"GarutVON helps every file workflow move faster.\"}"
```

The desktop update endpoint is `GET /api/version`.

## Donations

GarutVON is free to download. The support button opens MyHapper Smile at `https://myhappr.com/chisomlifeeugsh`; donations fund new features, bug fixes, infrastructure, AI services and long-term development.
