import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


def _events(database):
    db = sqlite3.connect(database)
    rows = db.execute("SELECT timestamp, track_id, zone, status, evidence FROM events ORDER BY timestamp DESC LIMIT 200").fetchall()
    db.close()
    return [{"timestamp": r[0], "track_id": r[1], "zone": r[2], "status": r[3], "evidence": r[4]} for r in rows]


def serve(database: str, host: str = "127.0.0.1", port: int = 8765):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/api/events":
                payload = json.dumps({"events": _events(database)}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
            elif path == "/health":
                payload = b'{"status":"ok"}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
            elif path == "/":
                payload = b"<html><head><title>CCTV SOP Monitor</title></head><body><h1>CCTV SOP Monitor</h1><p>Review events at <a href='/api/events'>/api/events</a>.</p><p>Statuses are evidence states and require human review.</p></body></html>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
            else:
                self.send_error(404)
                return
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_):
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"dashboard listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

