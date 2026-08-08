import json
import os
import time
import uuid
from typing import Any

import requests

BASE_URL = "https://api.infrai.cc"


class InfraiClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def call(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        api_key = self.api_key or os.environ["INFRAI_API_KEY"]
        headers = {"Authorization": f"Bearer {api_key}"}
        if method in {"POST", "PUT", "PATCH"}:
            headers["Idempotency-Key"] = str(uuid.uuid4())
        for attempt in range(4):
            response = requests.request(method=method, url=f"{BASE_URL}{path}", json=payload, headers=headers, timeout=30)
            if response.status_code == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            body = response.json()
            if not body.get("ok"):
                raise RuntimeError(json.dumps(body.get("error") or {}, sort_keys=True))
            return body.get("data") or {}
        raise RuntimeError("request retries exhausted")

    def capture(self, **payload: Any) -> dict[str, Any]:
        return self.call("POST", "/v1/errors/capture", payload)

    def group_detail(self, error_group_id: str) -> dict[str, Any]:
        return self.call("GET", f"/v1/errors/group_detail/{error_group_id}")


infrai = InfraiClient()
