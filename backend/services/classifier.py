"""Transparent heuristic classification of submitted problems."""

from enum import Enum


class ProblemClass(str, Enum):
    SYSTEM = "system_problem"
    CAUSAL = "causal_problem"
    DECISION = "decision_problem"
    ARGUMENT = "argument_problem"
    FORECASTING = "forecasting_problem"
    GENERAL_COMPLEX = "general_complex_problem"


CLASS_SIGNALS: dict[ProblemClass, tuple[str, ...]] = {
    ProblemClass.DECISION: (
        "should ",
        "choose",
        "option",
        "alternative",
        "hire now",
        " or wait",
        "decision",
    ),
    ProblemClass.CAUSAL: (
        "cause",
        "caused",
        "effect of",
        "lead to",
        "why ",
        "because",
        "result in",
    ),
    ProblemClass.ARGUMENT: (
        "argument",
        "claims",
        "claim that",
        "premise",
        "conclusion",
        "evidence for",
    ),
    ProblemClass.FORECASTING: (
        "forecast",
        "predict",
        "will ",
        "future",
        "next year",
        "likely to",
    ),
    ProblemClass.SYSTEM: (
        "system",
        "leaving",
        "young professionals",
        "increasing",
        "declining",
        "feedback",
        "stakeholder",
        "complex",
    ),
}

# Specific intent wins ties: an explicit argument or decision should not be
# swallowed by a causal word contained inside it.
CLASS_PRECEDENCE = (
    ProblemClass.ARGUMENT,
    ProblemClass.DECISION,
    ProblemClass.CAUSAL,
    ProblemClass.FORECASTING,
    ProblemClass.SYSTEM,
)


def classify_problem(problem: str) -> ProblemClass:
    """Classify text using inspectable substring signals and stable tie-breaking."""
    text = f" {problem.casefold().strip()} "
    scores = {
        problem_class: sum(signal in text for signal in signals)
        for problem_class, signals in CLASS_SIGNALS.items()
    }
    best_score = max(scores.values(), default=0)
    if best_score == 0:
        return ProblemClass.GENERAL_COMPLEX
    return next(item for item in CLASS_PRECEDENCE if scores[item] == best_score)
