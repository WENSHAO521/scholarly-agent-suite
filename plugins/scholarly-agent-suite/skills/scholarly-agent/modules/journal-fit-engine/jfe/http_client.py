"""Minimal, dependency-free HTTP client with an injectable transport so
tests never touch the network. Mirrors the pattern already established in
scholarly-corpus-builder/scb/http_client.py; not shared code (each Skill
repository stays independently installable), just the same shape.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Optional


class HttpError(Exception):
    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


@dataclass
class HttpResponse:
    status: int
    body: bytes

    def json(self):
        return json.loads(self.body.decode("utf-8"))


Transport = Callable[[str, dict], HttpResponse]


def _urllib_transport(url: str, headers: dict) -> HttpResponse:
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:  # noqa: S310 -- fixed https APIs only
            return HttpResponse(status=response.status, body=response.read())
    except urllib.error.HTTPError as exc:
        return HttpResponse(status=exc.code, body=exc.read())
    except urllib.error.URLError as exc:
        raise HttpError(f"network error: {exc.reason}") from exc


class HttpClient:
    """GET-only JSON client. Bounded retry on 429/5xx with a fixed backoff
    schedule; raises HttpError on exhaustion or a non-retryable status."""

    def __init__(self, user_agent: str, transport: Optional[Transport] = None,
                 max_retries: int = 2, backoff_seconds: float = 1.0):
        self.user_agent = user_agent
        self.transport = transport or _urllib_transport
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    def get_json(self, url: str):
        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        attempt = 0
        while True:
            response = self.transport(url, headers)
            if response.status == 200:
                return response.json()
            if response.status in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                time.sleep(self.backoff_seconds * (attempt + 1))
                attempt += 1
                continue
            raise HttpError(f"HTTP {response.status} for {url}", status=response.status)
