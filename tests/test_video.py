import cv2
import numpy as np

from cctv_monitor.models import Policy
from cctv_monitor.video import Detection, process_video


class FixedDetector:
    def detect(self, frame):
        return [Detection(10, 10, 60, 100, .9)]


def test_video_pipeline_writes_output_and_events(tmp_path):
    source = tmp_path / "input.mp4"
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"mp4v"), 5, (100, 120))
    for _ in range(3):
        writer.write(np.zeros((120, 100, 3), dtype=np.uint8))
    writer.release()
    output = tmp_path / "output.mp4"
    csv_path = tmp_path / "events.csv"
    frames = process_video(source, output, FixedDetector(), Policy("kitchen"), tmp_path / "events.sqlite3", csv_path)
    assert frames == 3
    assert output.stat().st_size > 0
    assert csv_path.read_text(encoding="utf-8").startswith("timestamp,track_id,zone,status,evidence")

