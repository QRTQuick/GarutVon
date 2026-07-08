import http.server
import socket
import threading
import urllib.parse
import webbrowser

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter.scrolledtext import ScrolledText

from .api_client import ApiClient
from .config import get_api_key, set_api_key
from .style import (
    ACCENT,
    BG,
    BORDER,
    CARD,
    CARD_SOFT,
    MUTED,
    TEXT,
    style_button,
    style_frame,
    style_label,
)


class BrowserLoginCallbackServer:
    def __init__(self) -> None:
        self.api_key: str | None = None
        self._server: http.server.HTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> int:
        handler = self._make_handler()
        self._server = http.server.HTTPServer(("127.0.0.1", 0), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self._server.server_address[1]

    def _make_handler(self):
        parent = self

        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path != "/callback":
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not found")
                    return

                query = urllib.parse.parse_qs(parsed.query)
                api_key_list = query.get("api_key", [])
                if not api_key_list:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Missing api_key")
                    return

                parent.api_key = api_key_list[0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h1>GarutVON login complete</h1><p>You may now return to the desktop application.</p></body></html>"
                )
                threading.Thread(target=self.server.shutdown, daemon=True).start()

            def log_message(self, format: str, *args: object) -> None:
                return

        return CallbackHandler

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
        if self._thread:
            self._thread.join(timeout=2)


class DesktopApp:
    def __init__(self, root: tk.Tk, api_client: ApiClient) -> None:
        self.root = root
        self.api = api_client
        # load saved API key from local config if present
        self.configured_api_key = get_api_key()
        if self.configured_api_key:
            self.api.set_api_key(self.configured_api_key)
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
        self.api_key_var = tk.StringVar(value=self.configured_api_key or "")

        self._make_field(frame, "Email", self.email_var)
        self._make_field(frame, "Password", self.password_var, show="*")
        self._make_field(frame, "API Key (paste here)", self.api_key_var)

        button = tk.Button(frame, text="Connect to API", command=self._handle_login)
        style_button(button)
        button.pack(pady=(20, 16))

        key_button = tk.Button(frame, text="Save API Key", command=self._handle_save_api_key)
        style_button(key_button)
        key_button.pack(pady=(0, 6))

        browser_button = tk.Button(frame, text="Login via Browser", command=self._handle_browser_login)
        style_button(browser_button)
        browser_button.pack(pady=(0, 6))

        self.login_status = tk.Label(
            frame,
            text="Enter your email/password or paste an API key to unlock the desktop tools.",
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
        self._make_action_button(right_panel, "Convert File", lambda: self._ask_file_and_call("Convert File"))
        self._make_action_button(right_panel, "OCR File", lambda: self._ask_file_and_call("OCR File"))
        self._make_action_button(right_panel, "Metadata", lambda: self._ask_file_and_call("Metadata"))
        self._make_action_button(right_panel, "Compress", lambda: self._ask_file_and_call("Compress"))
        self._make_action_button(right_panel, "Background Remove", lambda: self._ask_file_and_call("Background Remove"))

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
        api_key = self.api_key_var.get().strip()
        if api_key:
            # prefer API key if provided
            self.api.set_api_key(api_key)
            try:
                health = self.api.health()
                self.logged_in = True
                self.status_label.configure(
                    text=f"API status: connected ({health.get('status','ok')})"
                )
                self.api_details.configure(
                    text=f"Connected to {self.api.base_url}\nService version available."
                )
                # do not auto-save; user can press Save API Key
                self.login_container.pack_forget()
                self.main_container.pack(fill="both", expand=True, padx=0, pady=12)
                return
            except Exception as exc:
                messagebox.showerror(
                    "Connection error", f"API key connection failed:\n{exc}"
                )
                return

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

    def _handle_save_api_key(self) -> None:
        key = self.api_key_var.get().strip()
        if not key:
            messagebox.showwarning("Missing key", "Paste an API key before saving.")
            return
        set_api_key(key)
        self.api.set_api_key(key)
        messagebox.showinfo("Saved", "API key saved to local configuration.")

    def _handle_browser_login(self) -> None:
        try:
            callback_server = BrowserLoginCallbackServer()
            port = callback_server.start()
            base_url = self.api.base_url.rstrip("/")
            if base_url.endswith("/api"):
                web_url = base_url[: -len("/api")]
            else:
                web_url = base_url
            callback_url = f"http://127.0.0.1:{port}/callback"
            login_url = f"{web_url}/login?next={urllib.parse.quote(callback_url, safe='')}"
            webbrowser.open(login_url)
            self.login_status.configure(
                text="Waiting for browser login... Please complete login in the browser."
            )

            def check_callback() -> None:
                if callback_server.api_key:
                    api_key = callback_server.api_key
                    self.api_key_var.set(api_key)
                    self.api.set_api_key(api_key)
                    set_api_key(api_key)
                    callback_server.stop()
                    self._complete_browser_login()
                else:
                    self.root.after(500, check_callback)

            self.root.after(500, check_callback)
        except Exception as exc:
            messagebox.showerror("Browser login failed", f"{exc}")

    def _complete_browser_login(self) -> None:
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
            self.login_status.configure(
                text="Logged in via browser login."
            )
        except Exception as exc:
            messagebox.showerror("Connection error", f"Could not connect to API:\n{exc}")

    def _ask_file_and_call(self, action: str) -> None:
        file_path = filedialog.askopenfilename(title=action, filetypes=[("All files", "*")])
        if not file_path:
            return
        try:
            if action == "Convert File":
                target = simpledialog.askstring("Target format", "Enter target format (eg: pdf, docx, txt):")
                if not target:
                    return
                result = self.api.convert_file(file_path, target)
                messagebox.showinfo("Convert", f"Queued: {result}")
            elif action == "OCR File":
                result = self.api.ocr_file(file_path)
                messagebox.showinfo("OCR Result", f"Text length: {len(result.get('text',''))}")
            elif action == "Metadata":
                result = self.api.metadata_file(file_path)
                messagebox.showinfo("Metadata", f"{result}")
            elif action == "Compress":
                result = self.api.compress_file(file_path)
                messagebox.showinfo("Compress", f"{result}")
            elif action == "Background Remove":
                result = self.api.background_remove(file_path)
                messagebox.showinfo("Background Remove", f"{result}")
        except Exception as exc:
            messagebox.showerror(action + " failed", f"{exc}")

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
