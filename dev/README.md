# GarutVON Desktop Client

This folder contains a simple desktop client built with Tkinter that connects to the GarutVON API mounted at `/api`.

## Features
- Login-style app shell with a glassy black UI
- API health check and version fetch
- Text summarization via `/api/summarize`
- Modular code split across `api_client.py`, `ui.py`, `style.py`, and `run.py`

## Run

From the repo root, start the web server first, then run:

```powershell
python -m garutvon.desktop.run
```

## Notes
- The desktop app uses the existing `httpx` package already present in `requirements.txt`.
- The app is designed as a UI wrapper around the API endpoints rather than a full desktop auth system.
