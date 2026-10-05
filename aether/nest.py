"""NEST - Minimal WSGI-based HTTP framework."""
from __future__ import annotations
import json, re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


class Request:
    def __init__(self, method, path, query, headers, body):
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body
        self.params = {}

    def json(self):
        try:
            return json.loads(self.body.decode()) if self.body else {}
        except Exception:
            return {}


class Response:
    def __init__(self, body="", status=200, content_type="text/plain"):
        self.body = body
        self.status = status
        self.content_type = content_type
        self.headers = {}

    def json(self):
        self.content_type = "application/json"
        if not isinstance(self.body, (str, bytes)):
            self.body = json.dumps(self.body)
        return self


class Nest:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.routes = []
        self.middleware = []
        self._server = None

    def route(self, method, pattern):
        def decorator(fn):
            regex = re.compile("^" + re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", pattern) + "$")
            self.routes.append((method.upper(), regex, fn))
            return fn
        return decorator

    def get(self, pattern): return self.route("GET", pattern)
    def post(self, pattern): return self.route("POST", pattern)

    def use(self, fn):
        self.middleware.append(fn)
        return fn

    def _dispatch(self, req):
        for name, mw in enumerate(self.middleware):
            result = mw(req)
            if isinstance(result, Response):
                return result
        for method, regex, fn in self.routes:
            if method != req.method:
                continue
            m = regex.match(req.path)
            if m:
                req.params = m.groupdict()
                return fn(req)
        return Response("Not Found", status=404)

    def _make_handler(self):
        nest = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a): pass
            def _handle(self, method):
                parsed = urlparse(self.path)
                query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length) if length else b""
                req = Request(method, parsed.path, query, dict(self.headers), body)
                try:
                    resp = nest._dispatch(req)
                except Exception as e:
                    resp = Response(f"Error: {e}", status=500)
                if not isinstance(resp, Response):
                    resp = Response(str(resp))
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.content_type)
                for k, v in resp.headers.items():
                    self.send_header(k, v)
                self.end_headers()
                body = resp.body if isinstance(resp.body, bytes) else str(resp.body).encode()
                self.wfile.write(body)
            def do_GET(self): self._handle("GET")
            def do_POST(self): self._handle("POST")
        return Handler

    def start(self, blocking=True):
        self._server = HTTPServer((self.host, self.port), self._make_handler())
        if blocking:
            self._server.serve_forever()
        return self._server

    def stop(self):
        if self._server:
            self._server.shutdown()
