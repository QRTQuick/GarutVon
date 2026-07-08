"""GarutVON Developer Desktop Client

Single-file developer client that bundles API client, UI, and styles.
Run with: python dev/main.py
"""

from __future__ import annotations

import sys
import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

try:
    import httpx
except Exception as e:
    print("httpx is required. Install with: pip install httpx")
    raise

# Local dev config path
_LOCAL_CONFIG = Path.home() / ".garutvon_dev_config.json"


def _load_local_config() -> dict:
    try:
        if _LOCAL_CONFIG.exists():
            return json.loads(_LOCAL_CONFIG.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_local_api_key(key: str) -> None:
    cfg = _load_local_config()
    cfg["api_key"] = key
    try:
        _LOCAL_CONFIG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception:
        pass


def _get_local_api_key() -> str | None:
    return _load_local_config().get("api_key")

# -------------------- style.py (inlined) --------------------
BG = "#07070d"
CARD = "#11131d"
CARD_SOFT = "#1f2031"
TEXT = "#f5f5f7"
MUTED = "#9da3b8"
ACCENT = "#7fc7ff"
# Tkinter does not support 8-digit hex (alpha) here — use a 6-digit hex instead
BORDER = "#ffffff"


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
    def __init__(
        self, base_url: str = "http://127.0.0.1:5000/api", api_key: str | None = None
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.access_token: str | None = None
        self.client = httpx.Client(timeout=10.0)

    def set_api_key(self, api_key: str | None) -> None:
        self.api_key = api_key

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def health(self) -> dict:
        response = self.client.get(self._url("/health"), headers=self._headers())
        response.raise_for_status()
        return response.json()

    def version(self) -> dict:
        response = self.client.get(self._url("/version"), headers=self._headers())
        response.raise_for_status()
        return response.json()

    def summarize(self, text: str, target_language: str = "en") -> dict:
        payload = {"text": text, "target_language": target_language}
        response = self.client.post(
            self._url("/summarize"), json=payload, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def register(self, email: str, password: str) -> dict:
        payload = {"email": email, "password": password}
        response = self.client.post(
            self._url("/auth/register"), json=payload, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def login(self, email: str, password: str) -> dict:
        data = {"username": email, "password": password}
        response = self.client.post(
            self._url("/auth/token"), data=data, headers=self._headers()
        )
        response.raise_for_status()
        token_data = response.json()
        self.access_token = token_data.get("access_token")
        return token_data

    def forgot_password(self, email: str) -> dict:
        payload = {"email": email}
        response = self.client.post(
            self._url("/auth/forgot-password"), json=payload, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def reset_password(self, token: str, new_password: str) -> dict:
        payload = {"token": token, "new_password": new_password}
        response = self.client.post(
            self._url("/auth/reset-password"), json=payload, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def convert_file(self, file_path: str, target_format: str) -> dict:
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}
            data = {"target_format": target_format}
            response = self.client.post(
                self._url("/convert"), files=files, data=data, headers=self._headers()
            )
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
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5, relheight=0.65)
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
        self.api_key_var = tk.StringVar()

        self._make_field(frame, "Email", self.email_var)
        self._make_field(frame, "Password", self.password_var, show="*")
        self._make_field(frame, "API Key (optional)", self.api_key_var)

        button = tk.Button(frame, text="Connect to API", command=self._handle_login)
        style_button(button)
        button.pack(pady=(20, 10))

        register_button = tk.Button(frame, text="Register", command=self._handle_register)
        style_button(register_button)
        register_button.pack(pady=(0, 10))

        forgot_button = tk.Button(frame, text="Forgot Password?", command=self._handle_forgot_password)
        style_button(forgot_button)
        forgot_button.pack(pady=(0, 8))

        save_key_button = tk.Button(frame, text="Save API Key Locally", command=self._handle_save_api_key)
        style_button(save_key_button)
        save_key_button.pack(pady=(0, 8))

        reset_token_button = tk.Button(frame, text="Reset Password (token)", command=self._open_reset_dialog)
        style_button(reset_token_button)
        reset_token_button.pack(pady=(0, 8))

        self.login_status = tk.Label(
            frame,
            text="Use an API key or your account credentials to connect. Forgot password is supported.",
            bg=CARD,
            fg=MUTED,
            font=("Inter", 10),
            wraplength=380,
            justify="center",
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
        self._make_action_button(right_panel, "Convert File", self._choose_convert_file)
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

    def _make_text_action(self, parent: tk.Frame, text: str, command) -> None:
        label = tk.Label(parent, text=text, fg=ACCENT, bg=CARD, cursor="hand2")
        label.pack(padx=18, pady=6)
        label.bind("<Button-1>", lambda _: command())

    def _handle_login(self) -> None:
        api_key = self.api_key_var.get().strip()
        if api_key:
            self.api.set_api_key(api_key)
        else:
            email = self.email_var.get().strip()
            password = self.password_var.get().strip()
            if not email or not password:
                messagebox.showwarning(
                    "Missing fields", "Enter both email and password to continue."
                )
                return
            try:
                self.api.login(email, password)
            except Exception as exc:
                # Provide richer diagnostics for HTTP errors
                try:
                    import httpx

                    if isinstance(exc, httpx.HTTPStatusError):
                        resp = exc.response
                        messagebox.showerror(
                            "Login failed",
                            f"HTTP {resp.status_code}: {resp.text}",
                        )
                        return
                except Exception:
                    pass
                messagebox.showerror("Login failed", f"{exc}")
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

    def _handle_register(self) -> None:
        # open a simple register dialog
        dlg = tk.Toplevel(self.root)
        dlg.title("Register")
        dlg.geometry("420x220")
        style_frame(dlg)

        email_var = tk.StringVar()
        password_var = tk.StringVar()
        confirm_var = tk.StringVar()

        tk.Label(dlg, text="Email", bg=CARD, fg=TEXT).pack(anchor="w", padx=12, pady=(12, 0))
        tk.Entry(dlg, textvariable=email_var, bg="#141528", fg=TEXT).pack(fill="x", padx=12, pady=(4, 8))
        tk.Label(dlg, text="Password", bg=CARD, fg=TEXT).pack(anchor="w", padx=12, pady=(4, 0))
        tk.Entry(dlg, textvariable=password_var, show="*", bg="#141528", fg=TEXT).pack(fill="x", padx=12, pady=(4, 8))
        tk.Label(dlg, text="Confirm Password", bg=CARD, fg=TEXT).pack(anchor="w", padx=12, pady=(4, 0))
        tk.Entry(dlg, textvariable=confirm_var, show="*", bg="#141528", fg=TEXT).pack(fill="x", padx=12, pady=(4, 12))

        def _do_register():
            e = email_var.get().strip()
            p = password_var.get().strip()
            c = confirm_var.get().strip()
            if not e or not p:
                messagebox.showwarning("Missing fields", "Enter email and password.", parent=dlg)
                return
            if p != c:
                messagebox.showwarning("Mismatch", "Passwords do not match.", parent=dlg)
                return
            try:
                resp = self.api.register(e, p)
                messagebox.showinfo("Registered", f"Account created: {resp.get('email')}", parent=dlg)
                dlg.destroy()
            except Exception as exc:
                messagebox.showerror("Register failed", f"{exc}", parent=dlg)

        btn = tk.Button(dlg, text="Register", command=_do_register)
        style_button(btn)
        btn.pack(pady=(4, 12))

    def _handle_forgot_password(self) -> None:
        # open a small dialog to request password reset email
        email = self.email_var.get().strip()
        if not email:
            email = simpledialog.askstring("Forgot password", "Enter your account email:", parent=self.root)
            if not email:
                return
        try:
            response = self.api.forgot_password(email)
            messagebox.showinfo("Password reset", response.get("message", "Reset email sent."))
        except Exception as exc:
            messagebox.showerror("Forgot password failed", f"{exc}")

    def _handle_save_api_key(self) -> None:
        key = self.api_key_var.get().strip()
        if not key:
            messagebox.showwarning("Missing key", "Enter an API key to save locally.")
            return
        try:
            _save_local_api_key(key)
            self.api.set_api_key(key)
            messagebox.showinfo("Saved", "API key saved locally to ~/.garutvon_dev_config.json")
        except Exception as exc:
            messagebox.showerror("Save failed", f"{exc}")

    def _open_reset_dialog(self) -> None:
        dlg = tk.Toplevel(self.root)
        dlg.title("Reset Password (token)")
        dlg.geometry("420x200")
        style_frame(dlg)

        token_var = tk.StringVar()
        newpw_var = tk.StringVar()

        tk.Label(dlg, text="Reset Token", bg=CARD, fg=TEXT).pack(anchor="w", padx=12, pady=(12, 0))
        tk.Entry(dlg, textvariable=token_var, bg="#141528", fg=TEXT).pack(fill="x", padx=12, pady=(4, 8))
        tk.Label(dlg, text="New Password", bg=CARD, fg=TEXT).pack(anchor="w", padx=12, pady=(4, 0))
        tk.Entry(dlg, textvariable=newpw_var, show="*", bg="#141528", fg=TEXT).pack(fill="x", padx=12, pady=(4, 12))

        def _do_reset():
            t = token_var.get().strip()
            p = newpw_var.get().strip()
            if not t or not p:
                messagebox.showwarning("Missing fields", "Enter token and new password.", parent=dlg)
                return
            try:
                resp = self.api.reset_password(t, p)
                messagebox.showinfo("Password reset", resp.get("message", "Password changed."), parent=dlg)
                dlg.destroy()
            except Exception as exc:
                messagebox.showerror("Reset failed", f"{exc}", parent=dlg)

        btn = tk.Button(dlg, text="Reset Password", command=_do_reset)
        style_button(btn)
        btn.pack(pady=(4, 12))

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
        self.api_key_var.set("")
        self.api_details.configure(text="")
        self.main_container.pack_forget()
        self.login_container.pack(fill="both", expand=True, padx=22, pady=12)

    def _choose_convert_file(self) -> None:
        if not self.logged_in:
            messagebox.showwarning("Not connected", "Please connect to the API first.")
            return
        file_path = filedialog.askopenfilename(
            title="Convert File", filetypes=[("All files", "*")]
        )
        if not file_path:
            return
        target_format = tk.simpledialog.askstring(
            "Target format", "Enter target format (e.g. pdf, docx, txt):"
        )
        if not target_format:
            return
        try:
            result = self.api.convert_file(file_path, target_format)
            messagebox.showinfo("Conversion queued", f"{result}")
        except Exception as exc:
            messagebox.showerror("Conversion failed", f"{exc}")


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
