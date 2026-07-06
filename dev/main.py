"""GarutVON Developer Desktop Client

Single-file developer client that bundles API client, UI, and styles.
Run with: python dev/main.py
"""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

try:
    import httpx
except Exception as e:
    print("httpx is required. Install with: pip install httpx")
    raise

# -------------------- style.py (inlined) --------------------
BG = "#07070d"
CARD = "#11131d"
CARD_SOFT = "#1f2031"
TEXT = "#f5f5f7"
MUTED = "#9da3b8"
ACCENT = "#7fc7ff"
BORDER = "#ffffff22"


def style_frame(frame: tk.Frame) -> None:
    frame.configure(
        bg=CARD,
        bd=0,
        highlightbackground=BORDER,
        highlightthickness=1,
    )


def style_label(label: tk.Label, size: int = 11, bold: bool = False) -> None:
    label.configure(
        bg=CARD,
        fg=TEXT,
        font=("Inter", size, "bold" if bold else "normal"),
    )


def style_button(button: tk.Button) -> None:
    button.configure(
        bg="#1d1f2d",
        fg=TEXT,
        activebackground="#2c3048",
        activeforeground=TEXT,
        bd=0,
        highlightthickness=0,
        padx=14,
        pady=10,
        cursor="hand2",
    )


# -------------------- api_client.py (inlined) --------------------
class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:5000/api") -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=10.0)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def health(self) -> dict:
        response = self.client.get(self._url("/health"))
        response.raise_for_status()
        return response.json()

    def version(self) -> dict:
        response = self.client.get(self._url("/version"))
        response.raise_for_status()
        return response.json()

    def summarize(self, text: str, target_language: str = "en") -> dict:
        payload = {"text": text, "target_language": target_language}
        response = self.client.post(self._url("/summarize"), json=payload)
        response.raise_for_status()
        return response.json()


# -------------------- ui.py (inlined) --------------------
class DesktopApp:
    def __init__(self, root: tk.Tk, api_client: ApiClient) -> None:
        self.root = root
        self.api = api_client
        self.root.title("GarutVON Desktop Client")
        self.root.configure(bg=BG)
        self.root.geometry("980x660")
        self.root.minsize(900, 620)

        self.logged_in = False
        self._build_ui()

    def _build_ui(self) -> None:
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=22, pady=(18, 4))
        title = tk.Label(
            header, text="GarutVON Desktop", fg=TEXT, bg=BG, font=("Inter", 22, "bold")
        )
        title.pack(side="left")
        subtitle = tk.Label(
            header,
            text="Secure API client with glass-style layout",
            fg=MUTED,
            bg=BG,
            font=("Inter", 10),
        )
        subtitle.pack(side="left", padx=(16, 0), pady=(8, 0))

        self.login_container = tk.Frame(self.root, bg=BG)
        self.login_container.pack(fill="both", expand=True, padx=22, pady=12)
        self._build_login_view()

        self.main_container = tk.Frame(self.root, bg=BG)
        self._build_main_view()

    def _build_login_view(self) -> None:
        frame = tk.Frame(
            self.login_container,
            bg=CARD,
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5, relheight=0.55)
        style_frame(frame)

        label = tk.Label(
            frame,
            text="Login to GarutVON",
            bg=CARD,
            fg=TEXT,
            font=("Inter", 18, "bold"),
        )
        label.pack(pady=(24, 14))

        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self._make_field(frame, "Email", self.email_var)
        self._make_field(frame, "Password", self.password_var, show="*")

        button = tk.Button(frame, text="Connect to API", command=self._handle_login)
        style_button(button)
        button.pack(pady=(20, 16))

        self.login_status = tk.Label(
            frame,
            text="Enter your email and password to unlock the desktop tools.",
            bg=CARD,
            fg=MUTED,
            font=("Inter", 10),
        )
        self.login_status.pack(pady=(0, 12))

    def _build_main_view(self) -> None:
        self.main_container.configure(bg=BG)

        top_frame = tk.Frame(self.main_container, bg=BG)
        top_frame.pack(fill="x", padx=22, pady=(0, 12))

        self.status_label = tk.Label(
            top_frame,
            text="API status: disconnected",
            fg=ACCENT,
            bg=BG,
            font=("Inter", 10),
        )
        self.status_label.pack(anchor="w")

        content = tk.Frame(self.main_container, bg=BG)
        content.pack(fill="both", expand=True, padx=22, pady=(0, 18))

        left_panel = tk.Frame(
            content, bg=CARD, bd=0, highlightthickness=1, highlightbackground=BORDER
        )
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=4)
        style_frame(left_panel)

        right_panel = tk.Frame(
            content,
            bg=CARD_SOFT,
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        right_panel.pack(side="right", fill="both", expand=True, padx=(12, 0), pady=4)
        style_frame(right_panel)

        style_label(
            tk.Label(left_panel, text="Text Summarizer", font=("Inter", 16, "bold"))
        )
        tk.Label(
            left_panel,
            text="Paste a paragraph and click Summarize.",
            bg=CARD,
            fg=MUTED,
            font=("Inter", 10),
        ).pack(anchor="w", padx=18, pady=(0, 10))

        self.input_text = ScrolledText(
            left_panel,
            bg="#141528",
            fg=TEXT,
            insertbackground=TEXT,
            wrap="word",
            bd=0,
            relief="flat",
            font=("Inter", 11),
        )
        self.input_text.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        self.result_text = ScrolledText(
            left_panel,
            bg="#11131d",
            fg=TEXT,
            insertbackground=TEXT,
            wrap="word",
            bd=0,
            relief="flat",
            font=("Inter", 11),
            state="disabled",
        )
        self.result_text.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        summary_button = tk.Button(
            left_panel, text="Summarize Text", command=self._handle_summarize
        )
        style_button(summary_button)
        summary_button.pack(pady=(0, 20), padx=18, anchor="e")

        style_label(
            tk.Label(right_panel, text="Quick Actions", font=("Inter", 16, "bold"))
        )
        self._make_action_button(right_panel, "Check API Health", self._check_health)
        self._make_action_button(right_panel, "Fetch API Version", self._fetch_version)
        self._make_action_button(right_panel, "Reset Session", self._reset_app)

        self.api_details = tk.Label(
            right_panel,
            text="",
            bg=CARD_SOFT,
            fg=TEXT,
            justify="left",
            font=("Inter", 10),
            wraplength=240,
        )
        self.api_details.pack(fill="x", padx=18, pady=(18, 10))

    def _make_field(
        self,
        parent: tk.Frame,
        label_text: str,
        variable: tk.StringVar,
        show: str | None = None,
    ) -> None:
        label = tk.Label(
            parent, text=label_text, bg=CARD, fg=MUTED, font=("Inter", 10, "bold")
        )
        label.pack(anchor="w", padx=24, pady=(12, 0))
        entry = tk.Entry(
            parent,
            textvariable=variable,
            bg="#141528",
            fg=TEXT,
            insertbackground=TEXT,
            bd=0,
            relief="flat",
            font=("Inter", 12),
            show=show,
        )
        entry.pack(fill="x", padx=24, pady=(6, 0), ipady=10)

    def _make_action_button(self, parent: tk.Frame, text: str, command) -> None:
        button = tk.Button(parent, text=text, command=command)
        style_button(button)
        button.pack(fill="x", padx=18, pady=10)

    def _handle_login(self) -> None:
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        if not email or not password:
            messagebox.showwarning(
                "Missing fields", "Enter both email and password to continue."
            )
            return

        try:
            health = self.api.health()
            self.logged_in = True
            self.status_label.configure(
                text=f"API status: connected ({health.get('status','ok')})"
            )
            self.api_details.configure(
                text=f"Connected to {self.api.base_url}\nService version available."
            )
            self.login_container.pack_forget()
            self.main_container.pack(fill="both", expand=True, padx=0, pady=12)
        except Exception as exc:
            messagebox.showerror(
                "Connection error", f"Could not connect to API:\n{exc}"
            )

    def _handle_summarize(self) -> None:
        if not self.logged_in:
            messagebox.showwarning("Not connected", "Please connect to the API first.")
            return
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Empty text", "Enter some text before summarizing.")
            return
        try:
            response = self.api.summarize(text)
            self.result_text.configure(state="normal")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", response.get("summary", ""))
            self.result_text.configure(state="disabled")
            self.api_details.configure(
                text=f"Last summary: {response.get('sentence_count', 0)} sentences"
            )
        except Exception as exc:
            messagebox.showerror("API error", f"Summarization failed:\n{exc}")

    def _check_health(self) -> None:
        try:
            health = self.api.health()
            messagebox.showinfo(
                "API Health",
                f"{health.get('status','healthy')}\nService: {health.get('service','GarutVON API')}",
            )
        except Exception as exc:
            messagebox.showerror("Health check failed", f"{exc}")

    def _fetch_version(self) -> None:
        try:
            version = self.api.version()
            details = [
                f"Version: {version.get('latest_version')}",
                f"Download: {version.get('download_url')}",
                f"Checksum: {version.get('checksum')}",
            ]
            self.api_details.configure(text="\n".join(details))
        except Exception as exc:
            messagebox.showerror("Version check failed", f"{exc}")

    def _reset_app(self) -> None:
        self.logged_in = False
        self.email_var.set("")
        self.password_var.set("")
        self.api_details.configure(text="")
        self.main_container.pack_forget()
        self.login_container.pack(fill="both", expand=True, padx=22, pady=12)


# -------------------- run.py (inlined) --------------------


def main() -> None:
    root = tk.Tk()
    client = ApiClient()
    app = DesktopApp(root, client)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Fatal error while running the developer client:", exc)
        sys.exit(1)
