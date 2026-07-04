import os
from typing import Optional

import requests


class ReaBeClient:
    def __init__(self, base_url: str, api_token: Optional[str] = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self.session = requests.Session()

        if self.api_token:
            self.session.headers.update({"Authorization": f"Bearer {self.api_token}"})

    @classmethod
    def from_env(cls) -> Optional["ReaBeClient"]:
        base_url = os.getenv("REABE_BASE_URL", "").strip()
        if not base_url:
            return None

        api_token = os.getenv("REABE_API_TOKEN", "").strip() or None
        timeout = int(os.getenv("REABE_TIMEOUT", "10"))
        return cls(base_url=base_url, api_token=api_token, timeout=timeout)

    def get(self, endpoint: str = "/"):
        url = self.base_url + endpoint if endpoint.startswith("/") else f"{self.base_url}/{endpoint}"
        return self.session.get(url, timeout=self.timeout)
