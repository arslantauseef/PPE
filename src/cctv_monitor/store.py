import csv
import sqlite3
from pathlib import Path
from .models import Observation, Status


class EventStore:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, timestamp REAL, track_id INTEGER, zone TEXT, status TEXT, evidence TEXT)")
        self.db.commit()

    def add(self, observation: Observation, status: Status) -> None:
        evidence = ",".join(sorted(observation.detected_items))
        self.db.execute("INSERT INTO events(timestamp, track_id, zone, status, evidence) VALUES (?, ?, ?, ?, ?)", (observation.timestamp, observation.track_id, observation.zone, status.value, evidence))
        self.db.commit()

    def export_csv(self, path: str | Path) -> int:
        rows = self.db.execute("SELECT timestamp, track_id, zone, status, evidence FROM events ORDER BY timestamp").fetchall()
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "track_id", "zone", "status", "evidence"])
            writer.writerows(rows)
        return len(rows)

    def close(self) -> None:
        self.db.close()

