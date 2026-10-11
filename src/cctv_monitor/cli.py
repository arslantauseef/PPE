import argparse
from .models import Observation, Policy
from .rules import evaluate
from .store import EventStore


def demo(database: str, csv_path: str) -> None:
    policy = Policy(zone="kitchen", required_items=frozenset({"apron", "cap"}), persistence=2)
    observations = [
        Observation(1.0, 7, "kitchen", True, frozenset({"apron", "cap"}), .92),
        Observation(2.0, 7, "kitchen", True, frozenset({"apron"}), .91),
        Observation(3.0, 7, "kitchen", False, frozenset(), .2),
    ]
    store = EventStore(database)
    try:
        for item in observations:
            store.add(item, evaluate(item, policy))
        count = store.export_csv(csv_path)
    finally:
        store.close()
    print(f"wrote {count} synthetic events to {database} and {csv_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    demo_parser = sub.add_parser("demo")
    demo_parser.add_argument("--database", default="demo.sqlite3")
    demo_parser.add_argument("--csv", dest="csv_path", default="events.csv")
    args = parser.parse_args()
    if args.command == "demo":
        demo(args.database, args.csv_path)

