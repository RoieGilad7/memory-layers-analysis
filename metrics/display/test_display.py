from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from http.client import HTTPConnection
from threading import Event, Thread
from urllib.parse import urlencode
import unittest

from .report import render
from .server import _Viewer


def report(path):
    return {
        "checkpoint": path,
        "step": 3,
        "layer_index": 1,
        "device": "cpu",
        "metrics": {
            "Q1": {
                "title": "Next-token prediction",
                "columns": ["Subject", "NLL (nats)"],
                "rows": [["FreeLaw", 2.3456789]],
                "result": {},
            }
        },
    }


@contextmanager
def viewer(run):
    with _Viewer(report("first.pt"), run, 0) as server:
        thread = Thread(
            target=server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True
        )
        thread.start()
        try:
            yield server
        finally:
            server.shutdown()
            thread.join(timeout=2)


def request(server, path=None, origin=None, token=None):
    conn = HTTPConnection("127.0.0.1", server.server_port, timeout=4)
    try:
        if path is None:
            conn.request("GET", "/")
        else:
            conn.request(
                "POST",
                "/run",
                urlencode({"checkpoint": path, "token": token or server.token}),
                {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": origin or server.origin,
                },
            )
        response = conn.getresponse()
        return response.status, response.read().decode("utf-8")
    finally:
        conn.close()


class TestDisplay(unittest.TestCase):
    def test_static_output_and_escaping(self):
        page = render(report("<script>alert(1)</script>"))
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script>", page)
        self.assertNotIn("<form", page)
        self.assertIn("2.3457", page)

    def test_rerun_and_error_preserve_report(self):
        def run(path):
            if path == "bad.pt":
                raise ValueError("<missing weights>")
            return report(path)

        with viewer(run) as server:
            self.assertEqual(
                request(server, "blocked.pt", origin="http://example.org")[0], 403
            )
            self.assertEqual(request(server, "blocked.pt", token="invalid")[0], 403)
            self.assertEqual(request(server, "second file.pt")[0], 303)
            status, page = request(server, "bad.pt")
            self.assertEqual(status, 422)
            self.assertIn("&lt;missing weights&gt;", page)
            self.assertIn("second file.pt", page)
            self.assertEqual(server.report["checkpoint"], "second file.pt")

    def test_overlapping_run(self):
        entered, release = Event(), Event()

        def run(path):
            entered.set()
            release.wait(3)
            return report(path)

        with viewer(run) as server, ThreadPoolExecutor(max_workers=1) as executor:
            result = executor.submit(request, server, "second.pt")
            try:
                self.assertTrue(entered.wait(2))
                self.assertEqual(request(server, "third.pt")[0], 409)
                self.assertEqual(server.report["checkpoint"], "first.pt")
            finally:
                release.set()
            self.assertEqual(result.result()[0], 303)
