import httpx


class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:5000/api") -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=10.0)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def health(self) -> dict[str, str]:
        response = self.client.get(self._url("/health"))
        response.raise_for_status()
        return response.json()

    def version(self) -> dict[str, str]:
        response = self.client.get(self._url("/version"))
        response.raise_for_status()
        return response.json()

    def summarize(self, text: str, target_language: str = "en") -> dict[str, str]:
        payload = {"text": text, "target_language": target_language}
        response = self.client.post(self._url("/summarize"), json=payload)
        response.raise_for_status()
        return response.json()
