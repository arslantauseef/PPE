from dataclasses import dataclass, field
from enum import StrEnum
from typing import FrozenSet


class Status(StrEnum):
    COMPLIANT = "COMPLIANT"
    POSSIBLE_NONCOMPLIANCE = "POSSIBLE_NONCOMPLIANCE"
    UNKNOWN = "UNKNOWN"
    NOT_EVALUATED = "NOT_EVALUATED"


@dataclass(frozen=True)
class Observation:
    timestamp: float
    track_id: int
    zone: str
    visible: bool
    detected_items: FrozenSet[str] = field(default_factory=frozenset)
    confidence: float = 0.0


@dataclass(frozen=True)
class Policy:
    zone: str
    required_items: FrozenSet[str] = field(default_factory=frozenset)
    min_confidence: float = 0.5
    persistence: int = 3

