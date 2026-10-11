"""Recorded-video pipeline with a replaceable local detector and tracker."""
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .models import Observation, Policy
from .monitor import Monitor


@dataclass(frozen=True)
class Detection:
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    label: str = "person"


class Detector(Protocol):
    def detect(self, frame) -> list[Detection]: ...


class HOGPersonDetector:
    """OpenCV's built-in HOG people detector; no network or model download at runtime."""

    def __init__(self, hit_threshold: float = 0.0):
        import cv2
        self._hog = cv2.HOGDescriptor()
        self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.hit_threshold = hit_threshold

    def detect(self, frame) -> list[Detection]:
        boxes, weights = self._hog.detectMultiScale(frame, winStride=(8, 8), padding=(8, 8), scale=1.05)
        return [Detection(int(x), int(y), int(x + w), int(y + h), float(weight)) for (x, y, w, h), weight in zip(boxes, weights) if float(weight) >= self.hit_threshold]


class CentroidTracker:
    def __init__(self, max_distance: float = 80.0):
        self.next_id = 1
        self.centers: dict[int, tuple[float, float]] = {}
        self.max_distance = max_distance

    def update(self, detections: list[Detection]) -> list[tuple[int, Detection]]:
        import math
        remaining = set(self.centers)
        result = []
        for detection in detections:
            center = ((detection.x1 + detection.x2) / 2, (detection.y1 + detection.y2) / 2)
            candidate = min(remaining, key=lambda tid: math.dist(center, self.centers[tid]), default=None)
            if candidate is None or math.dist(center, self.centers[candidate]) > self.max_distance:
                candidate = self.next_id
                self.next_id += 1
            else:
                remaining.remove(candidate)
            self.centers[candidate] = center
            result.append((candidate, detection))
        self.centers = {tid: self.centers[tid] for tid, _ in result}
        return result


def process_video(source: str | int | Path, output: str | Path, detector: Detector, policy: Policy, database: str | Path, csv_path: str | Path, max_frames: int | None = None) -> int:
    """Process an MP4 locally and return the number of frames written."""
    import cv2
    from .store import EventStore
    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise RuntimeError(f"cannot open video source: {source}")
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    tracker = CentroidTracker()
    store = EventStore(database)
    monitor = Monitor(policy, store)
    frames = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            timestamp = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            tracked = tracker.update(detector.detect(frame))
            for track_id, detection in tracked:
                observation = Observation(timestamp, track_id, policy.zone, True, frozenset(), detection.confidence)
                event = monitor.consume(observation)
                color = (0, 180, 0) if event is None else (0, 0, 255)
                cv2.rectangle(frame, (detection.x1, detection.y1), (detection.x2, detection.y2), color, 2)
                cv2.putText(frame, f"person #{track_id} {detection.confidence:.2f}", (detection.x1, max(20, detection.y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, .55, color, 2)
            writer.write(frame)
            frames += 1
            if max_frames is not None and frames >= max_frames:
                break
    finally:
        capture.release()
        writer.release()
        store.export_csv(csv_path)
        store.close()
    return frames

