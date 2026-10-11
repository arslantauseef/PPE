from dataclasses import dataclass
from collections import defaultdict

from .models import Observation, Policy, Status
from .rules import evaluate
from .store import EventStore


@dataclass(frozen=True)
class ReviewEvent:
    timestamp: float
    track_id: int
    zone: str
    status: Status
    consecutive_frames: int


class Monitor:
    """Consumes detector observations and emits only persistent review events."""

    def __init__(self, policy: Policy, store: EventStore | None = None):
        self.policy = policy
        self.store = store
        self._counts: dict[tuple[int, str], int] = defaultdict(int)
        self._reported: set[tuple[int, str]] = set()

    def consume(self, observation: Observation) -> ReviewEvent | None:
        status = evaluate(observation, self.policy)
        key = (observation.track_id, observation.zone)
        if status == Status.POSSIBLE_NONCOMPLIANCE:
            self._counts[key] += 1
        else:
            self._counts[key] = 0
            self._reported.discard(key)
        if self.store:
            self.store.add(observation, status)
        if status != Status.POSSIBLE_NONCOMPLIANCE:
            return None
        if self._counts[key] < self.policy.persistence or key in self._reported:
            return None
        self._reported.add(key)
        return ReviewEvent(observation.timestamp, observation.track_id, observation.zone, status, self._counts[key])

