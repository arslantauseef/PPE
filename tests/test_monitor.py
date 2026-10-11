from cctv_monitor.models import Observation, Policy, Status
from cctv_monitor.monitor import Monitor


def obs(t, items=frozenset({"apron"})):
    return Observation(t, 4, "kitchen", True, items, .9)


def test_alert_requires_persistent_clear_observations():
    monitor = Monitor(Policy("kitchen", frozenset({"apron", "cap"}), persistence=2))
    assert monitor.consume(obs(1)) is None
    event = monitor.consume(obs(2))
    assert event is not None
    assert event.status == Status.POSSIBLE_NONCOMPLIANCE
    assert monitor.consume(obs(3)) is None


def test_compliance_resets_alert_debounce():
    monitor = Monitor(Policy("kitchen", frozenset({"apron", "cap"}), persistence=2))
    monitor.consume(obs(1))
    assert monitor.consume(obs(2)) is not None
    assert monitor.consume(obs(3, frozenset({"apron", "cap"}))) is None
    assert monitor.consume(obs(4)) is None
    assert monitor.consume(obs(5)) is not None

