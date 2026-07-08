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
curl http://127.0.0.1:5000/api/supported-formats
curl -X POST http://127.0.0.1:5000/api/convert -H "X-API-KEY: YOUR_KEY" -F "target_format=png" -F "file=@image.jpg"
```

The desktop update endpoint is `GET /api/version`.

## Packaging with PyOxidizer

The desktop client can be compiled into a standalone binary using PyOxidizer. A project config file is included at `pyoxidizer.bzl`.

```bash
python -m pip install pyoxidizer
pyoxidizer build --release --target-triple x86_64-unknown-linux-gnu
pyoxidizer build --release --target-triple x86_64-apple-darwin
pyoxidizer build --release --target-triple x86_64-pc-windows-msvc
```

On Windows, run the helper script:

```powershell
.\build_pyoxidizer.bat
```

On macOS/Linux, use:

```bash
./build_pyoxidizer.sh
```

The site download flow is connected to the packaged binary via `garutvon/backend/routes.py` and the `DOWNLOAD_URL_WINDOWS`, `DOWNLOAD_URL_MAC`, and `DOWNLOAD_URL_LINUX` environment variables.

## Donations

GarutVON is free to download. The support button opens MyHapper Smile at `https://myhappr.com/chisomlifeeugsh`; donations fund new features, bug fixes, infrastructure, AI services and long-term development.
