"""Shared HTTP engine (PART XIII): timeout, bounded retry, error
classification, and adapter availability states. Standard library only
(urllib) with a pluggable Transport so tests never touch the network.
"""

from __future__ import annotations

import json as _json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

AVAILABLE = "AVAILABLE"
DEGRADED = "DEGRADED"
RATE_LIMITED = "RATE_LIMITED"
AUTH_REQUIRED = "AUTH_REQUIRED"
UNAVAILABLE = "UNAVAILABLE"

_TRANSIENT_STATUS_CODES = {429, 502, 503, 504}


class HttpError(Exception):
    def __init__(self, message: str, status: Optional[int] = None, transient: bool = False, retry_after: Optional[float] = None):
        super().__init__(message)
        self.status = status
        self.transient = transient
        self.retry_after = retry_after


@dataclass
class HttpResponse:
    status: int
    headers: Dict[str, str]
    body: bytes
    url: str

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def json(self):
        return _json.loads(self.text())


Transport = Callable[[str, Dict[str, str], float], HttpResponse]


def urllib_transport(url: str, headers: Dict[str, str], timeout: float) -> HttpResponse:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return HttpResponse(status=resp.status, headers=dict(resp.headers), body=body, url=resp.geturl())
    except urllib.error.HTTPError as e:
        body = e.read() if hasattr(e, "read") else b""
        retry_after = None
        if e.headers and e.headers.get("Retry-After"):
            try:
                retry_after = float(e.headers.get("Retry-After"))
            except ValueError:
                retry_after = None
        transient = e.code in _TRANSIENT_STATUS_CODES
        raise HttpError("HTTP %d for %s" % (e.code, url), status=e.code, transient=transient, retry_after=retry_after) from e
    except urllib.error.URLError as e:
        raise HttpError("network error for %s: %s" % (url, e.reason), status=None, transient=True) from e


@dataclass
class RetryPolicy:
    max_retries: int = 3
    base_delay: float = 0.5
    max_delay: float = 8.0


@dataclass
class HttpClient:
    """Every adapter shares one of these. `transport` and `sleep_fn` are
    injectable so unit tests run instantly and offline."""

    user_agent: str
    timeout: float = 10.0
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    transport: Transport = urllib_transport
    sleep_fn: Callable[[float], None] = time.sleep

    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> HttpResponse:
        req_headers = {"User-Agent": self.user_agent}
        req_headers.update(headers or {})

        attempt = 0
        last_error: Optional[HttpError] = None
        while attempt <= self.retry_policy.max_retries:
            try:
                return self.transport(url, req_headers, self.timeout)
            except HttpError as e:
                last_error = e
                if not e.transient or attempt == self.retry_policy.max_retries:
                    raise
                delay = e.retry_after if e.retry_after is not None else min(
                    self.retry_policy.base_delay * (2 ** attempt), self.retry_policy.max_delay
                )
                self.sleep_fn(delay)
                attempt += 1
        raise last_error  # pragma: no cover — loop always returns or raises above


def classify_state(error: Optional[HttpError]) -> str:
    if error is None:
        return AVAILABLE
    if error.status == 429:
        return RATE_LIMITED
    if error.status in (401, 403):
        return AUTH_REQUIRED
    if error.transient:
        return DEGRADED
    return UNAVAILABLE
