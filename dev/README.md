# GarutVON Desktop Client

This folder contains a developer desktop client for GarutVON.

We've consolidated the example client into a single-file runner: `dev/main.py` which bundles the API client, UI and styling in one file for quick testing.

## Features
- Single-file Python/Tkinter client (`dev/main.py`) — run it directly with `python dev/main.py`.
- API health check and version fetch
- Text summarization via `/api/summarize`
- Simple glass-style UI for experimenting with endpoint calls

## Run

Start the backend web server first, then from the repo root run:

```powershell
python dev/main.py
```

## Notes
- The client requires `httpx` (install via `pip install httpx`).
- The single-file client is intended for local testing and exploration — not production distribution. It exercises the live API endpoints.
