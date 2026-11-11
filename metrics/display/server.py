"""Loopback report viewer. Only one checkpoint can be evaluated at a time."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import secrets
import threading
from urllib.parse import parse_qs
import webbrowser

from .report import render


class _Viewer(ThreadingHTTPServer):
    def __init__(self, report, run_checkpoint, port):
        super().__init__(("127.0.0.1", port), _Handler)
        self.report = report
        self.run_checkpoint = run_checkpoint
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.Lock()
        self.host = f"127.0.0.1:{self.server_port}"
        self.origin = f"http://{self.host}"


class _Handler(BaseHTTPRequestHandler):
    def _page(self, code, error=None, path=None):
        body = render(
            self.server.report, token=self.server.token, error=error, path=path
        ).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'; "
            "script-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'",
        )
        self.end_headers()
        self.wfile.write(body)

    def _local(self):
        if self.headers.get("Host") != self.server.host:
            self.send_error(403)
            return False
        return True

    def do_GET(self):
        if not self._local():
            return
        if self.path != "/":
            return self.send_error(404)
        self._page(200)

    def do_POST(self):
        if not self._local():
            return
        if self.path != "/run":
            return self.send_error(404)
        if self.headers.get("Origin", self.server.origin) != self.server.origin:
            return self.send_error(403)
        if self.headers.get_content_type() != "application/x-www-form-urlencoded":
            return self.send_error(415)
        try:
            size = int(self.headers.get("Content-Length", ""))
            if not 0 < size <= 16384:
                return self.send_error(413)
            fields = parse_qs(
                self.rfile.read(size).decode("utf-8"),
                keep_blank_values=True,
                strict_parsing=True,
                max_num_fields=2,
            )
        except (ValueError, UnicodeError):
            return self.send_error(400)
        if fields.get("token") != [self.server.token]:
            return self.send_error(403)
        paths = fields.get("checkpoint", [])
        if len(paths) != 1 or not paths[0].strip():
            return self._page(400, "Enter a checkpoint path.")
        path = paths[0].strip()
        if not self.server.lock.acquire(blocking=False):
            return self._page(409, "An evaluation is already running.", path)
        try:
            report = self.server.run_checkpoint(path)
            # Validate presentation before swapping the last successful report.
            render(report)
            self.server.report = report
        except (Exception, SystemExit) as exc:
            return self._page(422, str(exc) or type(exc).__name__, path)
        finally:
            self.server.lock.release()
        self.send_response(303)
        self.send_header("Location", "/")
        self.send_header("Content-Length", "0")
        self.end_headers()


def serve(initial_report, run_checkpoint, *, open_browser=True, port=0):
    """Serve until interrupted. The callback takes the edited checkpoint path."""
    render(initial_report)
    with _Viewer(initial_report, run_checkpoint, port) as server:
        print(f"Results: {server.origin}/  (Ctrl+C to stop)", flush=True)
        if open_browser:
            webbrowser.open(server.origin + "/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
