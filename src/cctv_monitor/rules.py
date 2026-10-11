from .models import Observation, Policy, Status


def evaluate(observation: Observation, policy: Policy) -> Status:
    """Evaluate one observation; absence of evidence is never treated as compliance."""
    if observation.zone != policy.zone:
        return Status.NOT_EVALUATED
    if not observation.visible or observation.confidence < policy.min_confidence:
        return Status.UNKNOWN
    if policy.required_items.issubset(observation.detected_items):
        return Status.COMPLIANT
    return Status.POSSIBLE_NONCOMPLIANCE

