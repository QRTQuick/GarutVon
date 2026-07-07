import json
from pathlib import Path
from typing import Optional

try:
    import keyring
except Exception:
    keyring = None


CONFIG_DIR = Path.home() / ".garutvon"
CONFIG_PATH = CONFIG_DIR / "config.json"


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _load_file_config() -> dict:
    _ensure_dir()
    if not CONFIG_PATH.exists():
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_file_config(data: dict) -> None:
    _ensure_dir()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


SERVICE_NAME = "GarutVON-Desktop"


def get_api_key() -> Optional[str]:
    """Return API key from OS keyring when available, else fallback to file config."""
    if keyring:
        try:
            val = keyring.get_password(SERVICE_NAME, "api_key")
            if val:
                return val
        except Exception:
            pass
    cfg = _load_file_config()
    return cfg.get("api_key")


def set_api_key(key: str) -> None:
    """Store API key in OS keyring when available; also write to file as fallback."""
    if keyring:
        try:
            keyring.set_password(SERVICE_NAME, "api_key", key)
        except Exception:
            # ignore keyring errors and fallback to file storage
            pass
    cfg = _load_file_config()
    cfg["api_key"] = key
    _save_file_config(cfg)


def get_base_url() -> str:
    cfg = _load_file_config()
    return cfg.get("base_url", "http://127.0.0.1:8000/api")


def set_base_url(url: str) -> None:
    cfg = _load_file_config()
    cfg["base_url"] = url
    _save_file_config(cfg)
