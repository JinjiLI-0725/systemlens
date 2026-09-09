"""Build deterministic plans from selected lens families."""

from backend.reasoning.operations import operations_for_lens
from backend.schemas.analysis import LensName


def plan_operations(lenses: list[LensName]) -> list[str]:
    """Expand lenses in user/selector order and remove duplicate operations."""
    plan: list[str] = []
    for lens in lenses:
        for operation in operations_for_lens(lens):
            if operation.id not in plan:
                plan.append(operation.id)
    return plan
