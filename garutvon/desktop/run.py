import os
import sys
from pathlib import Path

import tkinter as tk

if __name__ == "__main__" and __package__ is None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from garutvon.desktop.api_client import ApiClient
from garutvon.desktop.ui import DesktopApp
from garutvon.desktop.config import get_base_url, get_api_key


def main() -> None:
    root = tk.Tk()
    base = get_base_url()
    key = get_api_key()
    client = ApiClient(base_url=base, api_key=key)
    app = DesktopApp(root, client)
    root.mainloop()


if __name__ == "__main__":
    main()
