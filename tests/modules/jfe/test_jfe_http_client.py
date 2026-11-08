import unittest

from jfe.http_client import HttpClient, HttpError, HttpResponse


def scripted_transport(statuses, bodies=None):
    """Returns a transport that yields the given statuses in order, then
    keeps returning the last one."""
    calls = {"n": 0}
    bodies = bodies or {}

    def transport(url, headers):
        index = min(calls["n"], len(statuses) - 1)
        calls["n"] += 1
        status = statuses[index]
        body = bodies.get(index, b"{}")
        return HttpResponse(status=status, body=body)

    transport.calls = calls
    return transport


class HttpClientTests(unittest.TestCase):
    def test_success_returns_parsed_json(self):
        transport = scripted_transport([200], bodies={0: b'{"ok": true}'})
        client = HttpClient("agent", transport=transport, max_retries=0, backoff_seconds=0)
        self.assertEqual(client.get_json("https://example.test"), {"ok": True})

    def test_retries_on_429_then_succeeds(self):
        transport = scripted_transport([429, 200], bodies={1: b'{"ok": true}'})
        client = HttpClient("agent", transport=transport, max_retries=2, backoff_seconds=0)
        result = client.get_json("https://example.test")
        self.assertEqual(result, {"ok": True})
        self.assertEqual(transport.calls["n"], 2)

    def test_raises_after_exhausting_retries(self):
        transport = scripted_transport([503, 503, 503])
        client = HttpClient("agent", transport=transport, max_retries=2, backoff_seconds=0)
        with self.assertRaises(HttpError):
            client.get_json("https://example.test")

    def test_404_is_not_retried(self):
        transport = scripted_transport([404, 200])
        client = HttpClient("agent", transport=transport, max_retries=2, backoff_seconds=0)
        with self.assertRaises(HttpError):
            client.get_json("https://example.test")
        self.assertEqual(transport.calls["n"], 1)


if __name__ == "__main__":
    unittest.main()
