# GarutVON dekdev

A lightweight desktop client for GarutVON API conversion.

## Requirements

- Python 3.10+
- `httpx`
- `tkinter` (bundled with standard Python installs on Windows, macOS, and many Linux distributions)

Install dependencies:

```powershell
pip install httpx
```

## Run the client

```powershell
python dekdev/main.py
```

## Usage

1. Start the GarutVON server and ensure the API is available at `http://127.0.0.1:5000/api`.
2. Create an API key from the dashboard.
3. Enter the API URL and API key into the client.
4. Select a file to convert.
5. Enter a target format such as `png`, `jpg`, `webp`, `txt`, `md`, `html`, `csv`, `json`, `xml`, `yaml`, or `rtf`.
6. Press `Convert` and save the converted result.

## Notes

- The client uses the `X-API-KEY` header to authenticate with the GarutVON API.
- The conversion endpoint supports image format conversion and simple text file conversion.
