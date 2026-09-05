from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .app import ReviewEngineApp
from .configuration import load_configuration

MAX_BODY_BYTES = 1_000_000
WEB_ROOT = Path(__file__).with_name("web")
STATIC_ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


def static_asset(path: str) -> tuple[str, bytes] | None:
    """Return only explicitly allow-listed UI files; never map arbitrary paths."""
    spec = STATIC_ASSETS.get(path)
    if spec is None:
        return None
    filename, content_type = spec
    target = WEB_ROOT / filename
    return content_type, target.read_bytes()


class ReviewEngineHTTPHandler(BaseHTTPRequestHandler):
    app: ReviewEngineApp | None = None

    def _security_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; connect-src 'self'; img-src 'self' data:; "
            "style-src 'self'; script-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
        )

    def _bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self._bytes(status, body, "application/json; charset=utf-8")

    def _require_app(self) -> ReviewEngineApp:
        if self.app is None:
            raise RuntimeError("Review Engine application not configured")
        return self.app

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        asset = static_asset(path)
        if asset is not None:
            content_type, body = asset
            return self._bytes(200, body, content_type)

        app = self._require_app()
        try:
            if path == "/health":
                return self._json(200, app.health())
            if path == "/sessions":
                raw_limit = parse_qs(parsed.query).get("limit", ["100"])[0]
                return self._json(200, {"sessions": app.session_summaries(limit=int(raw_limit))})
            if path == "/memory":
                return self._json(200, {"records": app.current_memory()})
            if path.startswith("/sessions/") and path.endswith("/events"):
                session_id = path[len("/sessions/"):-len("/events")].strip("/")
                if not session_id:
                    return self._json(400, {"error": "session_id required"})
                return self._json(200, {"session_id": session_id, "events": app.session_events(session_id)})
            return self._json(404, {"error": "not found"})
        except (ValueError, TypeError) as exc:
            return self._json(400, {"error": str(exc)})
        except Exception:
            return self._json(500, {"error": "internal review-engine error"})

    def do_POST(self) -> None:
        app = self._require_app()
        path = urlparse(self.path).path
        if path != "/review":
            return self._json(404, {"error": "not found"})
        try:
            content_type = self.headers.get("Content-Type", "")
            if not content_type.lower().startswith("application/json"):
                return self._json(415, {"error": "application/json required"})
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                return self._json(400, {"error": "JSON request body required"})
            if length > MAX_BODY_BYTES:
                return self._json(413, {"error": "request body too large"})
            body = self.rfile.read(length)
            payload = json.loads(body.decode("utf-8"))
            if not isinstance(payload, dict):
                return self._json(400, {"error": "JSON object required"})
            return self._json(200, app.review(payload))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            return self._json(400, {"error": str(exc)})
        except Exception:
            # Do not return provider response bodies, credentials or internals to clients.
            return self._json(502, {"error": "review execution failed; inspect server evidence/logs"})

    def log_message(self, fmt: str, *args) -> None:
        # Standard request-line logging only; request bodies/API credentials are never logged.
        super().log_message(fmt, *args)


def serve(*, config_path: str, memory_db: str, sessions_db: str, host: str = "127.0.0.1", port: int = 8080) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("MVP HTTP server is local-only until authentication is implemented")
    configuration = load_configuration(config_path)
    ReviewEngineHTTPHandler.app = ReviewEngineApp(configuration, memory_db=memory_db, sessions_db=sessions_db)
    server = ThreadingHTTPServer((host, port), ReviewEngineHTTPHandler)
    print(f"Review Engine MVP listening on http://{host}:{port}")
    print(f"assurance_mode={configuration.assurance_mode}; action_execution_enabled=false")
    server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Local Review Engine MVP HTTP service")
    parser.add_argument("--config", required=True)
    parser.add_argument("--memory-db", default="review-engine-memory.db")
    parser.add_argument("--sessions-db", default="review-engine-sessions.db")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    serve(config_path=args.config, memory_db=args.memory_db, sessions_db=args.sessions_db, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
