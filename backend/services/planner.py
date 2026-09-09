"""Build deterministic plans from selected lens families."""

from backend.reasoning.operations import OPERATION_REGISTRY, operations_for_lens
from backend.schemas.analysis import LensName


def plan_operations(lenses: list[LensName]) -> list[str]:
    """Expand lenses in user/selector order and remove duplicate operations."""
    plan: list[str] = []
    for lens in lenses:
        for operation in operations_for_lens(lens):
            # Defense in depth: only entries in the active executable registry run.
            if operation.id in OPERATION_REGISTRY and operation.id not in plan:
                plan.append(operation.id)
    return plan
