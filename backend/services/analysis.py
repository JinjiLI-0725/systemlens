"""Orchestration and deterministic operation execution for SystemLens v0.1."""

import re

from backend.reasoning.operations import LENS_PURPOSES, operations_for_lens
from backend.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    Assumption,
    Claim,
    Confidence,
    ExecutionTrace,
    GraphEdge,
    GraphNode,
    LeveragePoint,
    LensName,
    SelectedLens,
    Unknown,
)
from backend.services.classifier import ProblemClass, classify_problem
from backend.services.lens_selector import select_lenses
from backend.services.planner import plan_operations

EVIDENCE_SIGNALS = (
    "according to",
    "data",
    "study",
    "survey",
    "research",
    "%",
    "measured",
    "sample",
)


def _subject(problem: str) -> str:
    return problem.rstrip(" ?.!")


def _confidence(problem: str, unknown_count: int) -> Confidence:
    evidence_count = sum(signal in problem.casefold() for signal in EVIDENCE_SIGNALS)
    score = min(0.62, max(0.18, 0.38 + evidence_count * 0.09 - unknown_count * 0.025))
    score = round(score, 2)
    level = "moderate" if score >= 0.5 else "low"
    evidence_note = (
        f"The text includes {evidence_count} evidence signal(s), but they have not been independently verified."
        if evidence_count
        else "The input supplies no explicit data or independently verified evidence."
    )
    return Confidence(
        score=score,
        level=level,
        rationale=f"{evidence_note} Outputs are preliminary hypotheses, and {unknown_count} material unknowns remain.",
    )


def _candidate_terms(problem: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", problem)
    ignored = {
        "what",
        "when",
        "where",
        "which",
        "does",
        "should",
        "could",
        "would",
        "why",
        "are",
        "the",
        "this",
        "that",
        "will",
        "now",
        "all",
        "and",
        "for",
        "six",
    }
    return [word for word in words if word.casefold() not in ignored][:5]


def _unknowns(problem_class: ProblemClass) -> list[Unknown]:
    items = [
        Unknown(
            question="What reliable evidence establishes the scale and baseline of the stated problem?",
            importance="high",
        ),
        Unknown(
            question="Which timeframe, population, geography, and exclusions define the scope?",
            importance="high",
        ),
        Unknown(
            question="Which observations would distinguish the leading hypothesis from alternatives?",
            importance="high",
        ),
    ]
    if problem_class == ProblemClass.DECISION:
        items.append(
            Unknown(
                question="What constraints, option values, and costs apply to each alternative?",
                importance="high",
            )
        )
    elif problem_class == ProblemClass.CAUSAL:
        items.append(
            Unknown(
                question="What confounders and temporal evidence affect the proposed causal direction?",
                importance="high",
            )
        )
    elif problem_class == ProblemClass.FORECASTING:
        items.append(
            Unknown(
                question="What base rate and leading indicators should anchor the forecast?",
                importance="high",
            )
        )
    return items


def _selected_lens_details(lenses: list[LensName]) -> list[SelectedLens]:
    return [
        SelectedLens(
            name=lens,
            purpose=LENS_PURPOSES[lens],
            operations=[operation.id for operation in operations_for_lens(lens)],
        )
        for lens in lenses
    ]


def build_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """Run classification, lens selection, planning, and template execution."""
    problem = request.problem.strip()
    problem_class = classify_problem(problem)
    lenses = select_lenses(problem_class, request.selected_lenses)
    plan = plan_operations(lenses)
    unknowns = _unknowns(problem_class)
    confidence = _confidence(problem, len(unknowns))
    terms = _candidate_terms(problem)
    actor_label = "Affected people or organizations"
    if terms:
        actor_label = " / ".join(terms[:2])

    assumptions = [
        Assumption(
            statement="Preliminary hypothesis: the wording accurately represents the underlying problem rather than one interpretation of it.",
            impact="A loaded or incomplete framing could direct analysis toward the wrong actors, causes, or options.",
            validation_question="How would neutral observers describe the problem, and where would they disagree?",
        ),
        Assumption(
            statement="Preliminary hypothesis: the most salient factors in the prompt are materially important.",
            impact="Unmentioned constraints or selection effects could explain the observed pattern.",
            validation_question="Which omitted variable would most weaken this initial framing?",
        ),
    ]
    if "detect_confounders" in plan:
        assumptions.append(
            Assumption(
                statement="Preliminary causal hypothesis: a shared external factor may influence both the proposed cause and effect.",
                impact="A confounder could make correlation look causal or exaggerate the relationship.",
                validation_question="Which factor precedes and predicts both sides of the proposed relationship?",
            )
        )
    if "run_pre_mortem" in plan:
        assumptions.append(
            Assumption(
                statement="Preliminary decision hypothesis: either option could fail if timing, capacity, or demand differs from expectations.",
                impact="Unexamined failure modes could make an apparently attractive option fragile.",
                validation_question="Imagine the chosen option failed: which early warning sign was missed?",
            )
        )

    graph_edges = [
        GraphEdge(
            source="boundary",
            target="actors",
            relationship="scopes",
            polarity="uncertain",
        ),
        GraphEdge(
            source="drivers",
            target="outcome",
            relationship="may influence (preliminary hypothesis)",
            polarity="uncertain",
        ),
        GraphEdge(
            source="actors",
            target="drivers",
            relationship="may shape and respond to",
            polarity="uncertain",
        ),
    ]
    if "detect_feedback_loops" in plan:
        graph_edges.append(
            GraphEdge(
                source="outcome",
                target="drivers",
                relationship="may feed back into (preliminary hypothesis)",
                polarity="uncertain",
            )
        )

    return AnalysisResponse(
        problem=problem,
        summary=(
            f"Preliminary {problem_class.value.replace('_', ' ')} analysis of: {_subject(problem)}. "
            "The items below are heuristic hypotheses to test, not established facts."
        ),
        selected_lenses=_selected_lens_details(lenses),
        claims=[
            Claim(
                statement=f"Preliminary claim under examination: {_subject(problem)}.",
                evidence=[
                    "The submitted wording is the only direct input; it is not corroborating evidence."
                ],
                confidence=confidence,
            )
        ],
        assumptions=assumptions,
        unknowns=unknowns,
        leverage_points=[
            LeveragePoint(
                title="Improve measurement before intervention",
                description="Define a baseline, segment affected actors, and collect evidence that can separate candidate explanations.",
                related_lens=LensName.CRITICAL_THINKING,
                priority="high",
            ),
            LeveragePoint(
                title="Test the highest-impact relationship",
                description="Run a small, reversible test of the most consequential candidate link before scaling a response.",
                related_lens=lenses[0],
                priority="medium",
            ),
        ],
        confidence=confidence,
        graph_nodes=[
            GraphNode(
                id="boundary",
                label="Provisional boundary",
                category="boundary",
                description="The actors and conditions named in the prompt, pending scope validation.",
            ),
            GraphNode(
                id="actors",
                label=actor_label,
                category="actor",
                description="Candidate actors inferred from prompt terms; identities and roles require validation.",
            ),
            GraphNode(
                id="drivers",
                label="Candidate drivers",
                category="variable",
                description="Incentives, constraints, alternatives, and external conditions may contribute.",
            ),
            GraphNode(
                id="outcome",
                label="Stated outcome",
                category="outcome",
                description=_subject(problem),
            ),
        ],
        graph_edges=graph_edges,
        execution_trace=ExecutionTrace(
            problem_class=problem_class.value, selected_lenses=lenses, operations=plan
        ),
    )


# Compatibility for internal callers that used the v0 mock function name.
build_mock_analysis = build_analysis
