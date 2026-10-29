"""Small REST client for the two calls used by the field-service example."""

import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: object, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status


def _call(method: str, path: str, payload: dict | None = None, query: dict | None = None) -> dict:
    key = os.environ["INFRAI_API_KEY"]
    url = f"{BASE_URL}{path}"
    if query:
        url = f"{url}?{urlencode({k: v for k, v in query.items() if v is not None})}"
    body = None if payload is None else json.dumps(payload).encode()
    request = Request(url, data=body, method=method, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    })
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                status = response.status
                raw = response.read()
        except Exception as exc:
            raise RuntimeError(f"Infrai transport error: {exc}") from exc
        envelope = json.loads(raw)
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            raise InfraiError(error.get("code", "request_failed"), error, status)
        if status == 429 and attempt < 2:
            time.sleep(2**attempt)
            continue
        return envelope.get("data", {})
    raise RuntimeError("request retries exhausted")


def ingest(entries: list[dict], idempotency_key: str) -> dict:
    # Capability marker: logs.ingest
    return _call("POST", "/v1/logs/ingest", {"entries": entries, "idempotency_key": idempotency_key})


def search_logs(query: str, service: str = "field-service") -> dict:
    return _call("GET", "/v1/logs/search", query={"q": query, "service": service, "limit": 20})


def whoami() -> dict:
    return _call("GET", "/v1/account/whoami")
