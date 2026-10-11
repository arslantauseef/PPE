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
                payload = b'''<!doctype html><html><head><meta charset="utf-8"><title>CCTV SOP Monitor</title><style>body{font:16px sans-serif;max-width:1000px;margin:2em auto;background:#f6f7f9;color:#17202a} .cards{display:flex;gap:1em}.card{background:white;padding:1em;border-radius:8px;flex:1;box-shadow:0 1px 4px #ccd} table{width:100%;background:white;border-collapse:collapse;margin-top:1em}td,th{padding:.7em;border-bottom:1px solid #ddd;text-align:left}.COMPLIANT{color:green}.POSSIBLE_NONCOMPLIANCE{color:#b00}.UNKNOWN{color:#a60}</style></head><body><h1>CCTV SOP Monitor</h1><p>Local review dashboard. Events are evidence states and require human review.</p><div id="cards" class="cards"></div><table><thead><tr><th>Time</th><th>Track</th><th>Zone</th><th>Status</th><th>Evidence</th></tr></thead><tbody id="rows"></tbody></table><script>async function refresh(){const d=await (await fetch('/api/events')).json(),e=d.events,c={};e.forEach(x=>c[x.status]=(c[x.status]||0)+1);document.getElementById('cards').innerHTML=Object.entries(c).map(([k,v])=>`<div class="card"><b>${k}</b><br><span>${v} observations</span></div>`).join('');document.getElementById('rows').innerHTML=e.map(x=>`<tr><td>${x.timestamp.toFixed(2)}</td><td>${x.track_id}</td><td>${x.zone}</td><td class="${x.status}"><b>${x.status}</b></td><td>${x.evidence||'none'}</td></tr>`).join('')}refresh();setInterval(refresh,2000)</script></body></html>'''
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

