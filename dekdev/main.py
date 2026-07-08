"""GarutVON dekdev desktop client.

This lightweight desktop application uses the site-issued API key to upload files
and receive converted output from the `/api/convert` endpoint.

Run with:
    python dekdev/main.py
"""

from __future__ import annotations
import base64
import json
import os
import io
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

try:
    import httpx
except ImportError as exc:
    raise SystemExit('httpx is required. Install with: pip install httpx') from exc

CONFIG_PATH = Path.home() / '.garutvon_dekdev.json'
DEFAULT_API_URL = 'http://127.0.0.1:5000/api'


def load_settings() -> dict:
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    except Exception:
        pass
    return {}


def save_settings(settings: dict) -> None:
    try:
        CONFIG_PATH.write_text(json.dumps(settings, indent=2), encoding='utf-8')
    except Exception:
        pass


class ApiClient:
    def __init__(self, base_url: str = DEFAULT_API_URL, api_key: str | None = None) -> None:
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.Client(timeout=30.0)

    def headers(self) -> dict:
        headers = {'Accept': 'application/json'}
        if self.api_key:
            headers['X-API-KEY'] = self.api_key
        return headers

    def health(self) -> dict:
        response = self.client.get(f'{self.base_url}/health', headers=self.headers())
        response.raise_for_status()
        return response.json()

    def supported_formats(self) -> dict:
        response = self.client.get(f'{self.base_url}/supported-formats', headers=self.headers())
        response.raise_for_status()
        return response.json()

    def convert_file(self, file_path: str, target_format: str) -> dict:
        with open(file_path, 'rb') as stream:
            files = {'file': (Path(file_path).name, stream)}
            data = {'target_format': target_format}
            response = self.client.post(
                f'{self.base_url}/convert', files=files, data=data, headers=self.headers()
            )
        response.raise_for_status()
        return response.json()


class DesktopApp:
    def __init__(self, root: tk.Tk, client: ApiClient) -> None:
        self.root = root
        self.client = client
        self.root.title('GarutVON dekdev Client')
        self.root.geometry('940x680')
        self.root.configure(bg='#11131d')
        self.file_path = tk.StringVar()
        self.target_format = tk.StringVar()
        self.api_key = tk.StringVar()
        self.api_url = tk.StringVar()
        self._load_config()
        self._build_ui()

    def _load_config(self) -> None:
        settings = load_settings()
        self.api_key.set(settings.get('api_key', ''))
        self.api_url.set(settings.get('api_url', DEFAULT_API_URL))

    def _save_config(self) -> None:
        save_settings({'api_key': self.api_key.get(), 'api_url': self.api_url.get()})

    def _build_ui(self) -> None:
        header = tk.Frame(self.root, bg='#0f1220')
        header.pack(fill='x', padx=16, pady=(16, 8))
        tk.Label(header, text='GarutVON dekdev', fg='#f5f5f7', bg='#0f1220', font=('Inter', 20, 'bold')).pack(side='left')
        tk.Label(header, text='API conversion client', fg='#9da3b8', bg='#0f1220', font=('Inter', 10)).pack(side='left', padx=(12, 0), pady=8)

        frame = tk.Frame(self.root, bg='#11131d')
        frame.pack(fill='x', padx=16, pady=8)

        tk.Label(frame, text='API URL:', fg='#f5f5f7', bg='#11131d').grid(row=0, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.api_url, width=64, bg='#1f2031', fg='#f5f5f7', insertbackground='#f5f5f7').grid(row=0, column=1, sticky='we', padx=8, pady=4)
        tk.Button(frame, text='Save', command=self._save_config, bg='#1f2438', fg='#f5f5f7', bd=0).grid(row=0, column=2, padx=8)

        tk.Label(frame, text='API Key:', fg='#f5f5f7', bg='#11131d').grid(row=1, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.api_key, width=64, bg='#1f2031', fg='#f5f5f7', insertbackground='#f5f5f7').grid(row=1, column=1, sticky='we', padx=8, pady=4)
        tk.Button(frame, text='Check API', command=self.check_api, bg='#1f2438', fg='#f5f5f7', bd=0).grid(row=1, column=2, padx=8)

        tk.Label(frame, text='File:', fg='#f5f5f7', bg='#11131d').grid(row=2, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.file_path, width=64, bg='#1f2031', fg='#f5f5f7', insertbackground='#f5f5f7').grid(row=2, column=1, sticky='we', padx=8, pady=4)
        tk.Button(frame, text='Browse', command=self.choose_file, bg='#1f2438', fg='#f5f5f7', bd=0).grid(row=2, column=2, padx=8)

        tk.Label(frame, text='Target format:', fg='#f5f5f7', bg='#11131d').grid(row=3, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.target_format, width=20, bg='#1f2031', fg='#f5f5f7', insertbackground='#f5f5f7').grid(row=3, column=1, sticky='w', padx=8, pady=4)
        tk.Button(frame, text='Convert', command=self.convert_file, bg='#4f8cff', fg='#f5f5f7', bd=0, padx=18).grid(row=3, column=2, padx=8)

        frame.columnconfigure(1, weight=1)

        self.log_output = ScrolledText(self.root, bg='#0f1220', fg='#e6edf9', insertbackground='#e6edf9', bd=0, highlightthickness=0)
        self.log_output.pack(fill='both', expand=True, padx=16, pady=(4, 16))
        self.log('Ready. Select a file, enter a target format, and press Convert.')

    def log(self, message: str) -> None:
        self.log_output.insert('end', message + '\n')
        self.log_output.see('end')

    def choose_file(self) -> None:
        selection = filedialog.askopenfilename(title='Choose file to convert')
        if selection:
            self.file_path.set(selection)
            self.log(f'Selected file: {selection}')

    def check_api(self) -> None:
        self.client.api_key = self.api_key.get().strip()
        self.client.base_url = self.api_url.get().strip().rstrip('/')
        try:
            data = self.client.health()
            self.log(f'API OK: {data}')
            messagebox.showinfo('API Check', 'Connected to GarutVON API successfully.')
        except Exception as exc:
            self.log(f'API error: {exc}')
            messagebox.showerror('API Check', f'Unable to reach API: {exc}')

    def convert_file(self) -> None:
        file_path = self.file_path.get().strip()
        target_format = self.target_format.get().strip().lower()
        if not file_path or not target_format:
            messagebox.showwarning('Missing values', 'Please select a file and enter a target format.')
            return
        if not Path(file_path).exists():
            messagebox.showwarning('File not found', 'Please select a valid file path.')
            return

        self.client.api_key = self.api_key.get().strip()
        self.client.base_url = self.api_url.get().strip().rstrip('/')

        try:
            self.log(f'Converting {file_path} → {target_format}')
            result = self.client.convert_file(file_path, target_format)
            content = base64.b64decode(result['converted_base64'])
            suggested = Path(result.get('filename', Path(file_path).stem + '.' + target_format))
            save_path = filedialog.asksaveasfilename(
                title='Save converted file',
                defaultextension='.' + suggested.suffix.lstrip('.'),
                initialfile=suggested.name,
                filetypes=[('All files', '*.*')],
            )
            if not save_path:
                self.log('Save cancelled by user.')
                return
            Path(save_path).write_bytes(content)
            self.log(f'Saved converted file to {save_path}')
            messagebox.showinfo('Conversion complete', f'Converted file saved to:\n{save_path}')
        except Exception as exc:
            self.log(f'Conversion failed: {exc}')
            messagebox.showerror('Conversion error', f'Conversion failed: {exc}')


def main() -> None:
    root = tk.Tk()
    client = ApiClient()
    app = DesktopApp(root, client)
    root.mainloop()


if __name__ == '__main__':
    main()
