import httpx
from typing import Optional


class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api", api_key: Optional[str] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.Client(timeout=30.0)

    def set_api_key(self, key: Optional[str]) -> None:
        self.api_key = key

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
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
        response = self.client.post(self._url("/summarize"), json=payload, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def convert_file(self, file_path: str, target_format: str) -> dict:
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}
            data = {"target_format": target_format}
            response = self.client.post(self._url("/convert"), files=files, data=data, headers=self._headers())
            response.raise_for_status()
            return response.json()

    def ocr_file(self, file_path: str) -> dict:
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}
            response = self.client.post(self._url("/ocr"), files=files, headers=self._headers())
            response.raise_for_status()
            return response.json()

    def metadata_file(self, file_path: str) -> dict:
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}
            response = self.client.post(self._url("/metadata"), files=files, headers=self._headers())
            response.raise_for_status()
            return response.json()

    def compress_file(self, file_path: str) -> dict:
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}
            response = self.client.post(self._url("/compress"), files=files, headers=self._headers())
            response.raise_for_status()
            return response.json()

    def background_remove(self, file_path: str) -> dict:
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}
            response = self.client.post(self._url("/background-remove"), files=files, headers=self._headers())
            response.raise_for_status()
            return response.json()

