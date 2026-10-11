from cctv_monitor.models import Observation, Policy, Status
from cctv_monitor.rules import evaluate


def test_compliant_requires_all_items():
    policy = Policy("kitchen", frozenset({"apron", "cap"}))
    assert evaluate(Observation(1, 1, "kitchen", True, frozenset({"apron", "cap"}), .9), policy) == Status.COMPLIANT


def test_missing_item_is_reviewable_noncompliance():
    policy = Policy("kitchen", frozenset({"apron", "cap"}))
    assert evaluate(Observation(1, 1, "kitchen", True, frozenset({"apron"}), .9), policy) == Status.POSSIBLE_NONCOMPLIANCE


def test_low_visibility_is_unknown():
    policy = Policy("kitchen", frozenset({"apron"}))
    assert evaluate(Observation(1, 1, "kitchen", False, frozenset(), .99), policy) == Status.UNKNOWN


def test_wrong_zone_is_not_evaluated():
    policy = Policy("kitchen", frozenset({"apron"}))
    assert evaluate(Observation(1, 1, "entrance", True, frozenset({"apron"}), .99), policy) == Status.NOT_EVALUATED

