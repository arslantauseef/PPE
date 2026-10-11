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
    video_parser = sub.add_parser("video", help="process an MP4 with the local OpenCV person detector")
    video_parser.add_argument("source")
    video_parser.add_argument("--output", default="annotated.mp4")
    video_parser.add_argument("--database", default="events.sqlite3")
    video_parser.add_argument("--csv", dest="csv_path", default="events.csv")
    video_parser.add_argument("--zone", default="unconfigured")
    video_parser.add_argument("--persistence", type=int, default=3)
    video_parser.add_argument("--max-frames", type=int, default=None, help="stop after N frames; useful for live-camera smoke tests")
    dashboard_parser = sub.add_parser("dashboard", help="serve local event API and review page")
    dashboard_parser.add_argument("--database", default="events.sqlite3")
    dashboard_parser.add_argument("--host", default="127.0.0.1")
    dashboard_parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.command == "demo":
        demo(args.database, args.csv_path)
    elif args.command == "video":
        from .video import HOGPersonDetector, process_video
        source = int(args.source) if args.source.isdigit() else args.source
        frames = process_video(source, args.output, HOGPersonDetector(), Policy(args.zone, persistence=args.persistence), args.database, args.csv_path, args.max_frames)
        print(f"processed {frames} frames; wrote {args.output}, {args.database}, and {args.csv_path}")
    elif args.command == "dashboard":
        from .dashboard import serve
        serve(args.database, args.host, args.port)

