import os
import sys
import unittest


from scb.http_client import (
    AUTH_REQUIRED,
    AVAILABLE,
    DEGRADED,
    RATE_LIMITED,
    HttpClient,
    HttpError,
    HttpResponse,
    RetryPolicy,
    classify_state,
)


def _make_scripted_transport(script):
    """script: list of callables or HttpResponse/HttpError to return in order."""
    calls = {"count": 0}

    def transport(url, headers, timeout):
        step = script[calls["count"]]
        calls["count"] += 1
        if isinstance(step, Exception):
            raise step
        return step

    transport.calls = calls
    return transport


class TestHttpClientRetry(unittest.TestCase):
    def test_succeeds_first_try(self):
        transport = _make_scripted_transport([HttpResponse(200, {}, b"ok", "http://x")])
        client = HttpClient(user_agent="test/1.0", transport=transport, sleep_fn=lambda s: None)
        resp = client.get("http://x")
        self.assertEqual(resp.status, 200)

    def test_retries_transient_error_then_succeeds(self):
        sleeps = []
        script = [
            HttpError("boom", status=503, transient=True),
            HttpResponse(200, {}, b"ok", "http://x"),
        ]
        transport = _make_scripted_transport(script)
        client = HttpClient(
            user_agent="test/1.0",
            transport=transport,
            sleep_fn=lambda s: sleeps.append(s),
            retry_policy=RetryPolicy(max_retries=2, base_delay=0.1),
        )
        resp = client.get("http://x")
        self.assertEqual(resp.status, 200)
        self.assertEqual(len(sleeps), 1)

    def test_does_not_retry_permanent_error(self):
        script = [HttpError("not found", status=404, transient=False)]
        transport = _make_scripted_transport(script)
        client = HttpClient(user_agent="test/1.0", transport=transport, sleep_fn=lambda s: None)
        with self.assertRaises(HttpError):
            client.get("http://x")
        self.assertEqual(transport.calls["count"], 1)

    def test_gives_up_after_max_retries(self):
        script = [
            HttpError("boom", status=503, transient=True),
            HttpError("boom", status=503, transient=True),
            HttpError("boom", status=503, transient=True),
        ]
        transport = _make_scripted_transport(script)
        client = HttpClient(
            user_agent="test/1.0",
            transport=transport,
            sleep_fn=lambda s: None,
            retry_policy=RetryPolicy(max_retries=2, base_delay=0.01),
        )
        with self.assertRaises(HttpError):
            client.get("http://x")
        self.assertEqual(transport.calls["count"], 3)

    def test_honors_retry_after_header(self):
        sleeps = []
        script = [
            HttpError("rate limited", status=429, transient=True, retry_after=2.5),
            HttpResponse(200, {}, b"ok", "http://x"),
        ]
        transport = _make_scripted_transport(script)
        client = HttpClient(
            user_agent="test/1.0",
            transport=transport,
            sleep_fn=lambda s: sleeps.append(s),
            retry_policy=RetryPolicy(max_retries=2, base_delay=0.1),
        )
        client.get("http://x")
        self.assertEqual(sleeps, [2.5])


class TestClassifyState(unittest.TestCase):
    def test_no_error_is_available(self):
        self.assertEqual(classify_state(None), AVAILABLE)

    def test_429_is_rate_limited(self):
        self.assertEqual(classify_state(HttpError("x", status=429, transient=True)), RATE_LIMITED)

    def test_401_403_is_auth_required(self):
        self.assertEqual(classify_state(HttpError("x", status=401)), AUTH_REQUIRED)
        self.assertEqual(classify_state(HttpError("x", status=403)), AUTH_REQUIRED)

    def test_transient_other_is_degraded(self):
        self.assertEqual(classify_state(HttpError("x", status=503, transient=True)), DEGRADED)


if __name__ == "__main__":
    unittest.main()
