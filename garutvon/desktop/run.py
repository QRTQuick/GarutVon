import tkinter as tk

from .api_client import ApiClient
from .ui import DesktopApp
from .config import get_base_url, get_api_key


def main() -> None:
    root = tk.Tk()
    base = get_base_url()
    key = get_api_key()
    client = ApiClient(base_url=base, api_key=key)
    app = DesktopApp(root, client)
    root.mainloop()


if __name__ == "__main__":
    main()
