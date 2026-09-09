"""Lens selection rules for each problem class."""

from backend.schemas.analysis import LensName
from backend.services.classifier import ProblemClass

CLASS_LENSES: dict[ProblemClass, tuple[LensName, ...]] = {
    ProblemClass.SYSTEM: (LensName.SYSTEMS_THINKING, LensName.CRITICAL_THINKING),
    ProblemClass.CAUSAL: (LensName.CAUSAL_REASONING, LensName.CRITICAL_THINKING),
    ProblemClass.DECISION: (
        LensName.DECISION_MAKING,
        LensName.CRITICAL_THINKING,
        LensName.METACOGNITION_AND_BIAS,
    ),
    ProblemClass.ARGUMENT: (
        LensName.CRITICAL_THINKING,
        LensName.METACOGNITION_AND_BIAS,
    ),
    ProblemClass.FORECASTING: (
        LensName.FORECASTING,
        LensName.CRITICAL_THINKING,
        LensName.PROBABILISTIC_THINKING,
    ),
    ProblemClass.GENERAL_COMPLEX: (
        LensName.PROBLEM_SOLVING,
        LensName.CRITICAL_THINKING,
    ),
}


def select_lenses(
    problem_class: ProblemClass, requested: list[LensName] | None = None
) -> list[LensName]:
    """Respect an explicit request; otherwise apply the class mapping."""
    return (
        list(requested) if requested is not None else list(CLASS_LENSES[problem_class])
    )
