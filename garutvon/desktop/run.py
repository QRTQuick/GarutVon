import tkinter as tk

from .api_client import ApiClient
from .ui import DesktopApp


def main() -> None:
    root = tk.Tk()
    app = DesktopApp(root, ApiClient())
    root.mainloop()


if __name__ == "__main__":
    main()
