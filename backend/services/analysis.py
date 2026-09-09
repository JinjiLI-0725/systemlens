"""Deterministic analysis logic used until an analysis engine is introduced."""

from backend.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    Assumption,
    Claim,
    Confidence,
    GraphEdge,
    GraphNode,
    LeveragePoint,
    LensName,
    SelectedLens,
    Unknown,
)

LENS_DEFINITIONS: dict[LensName, tuple[str, list[str]]] = {
    LensName.SYSTEMS_THINKING: (
        "Understand structure, interactions, feedback, boundaries and leverage points.",
        ["Define system boundary", "Map relationships", "Identify leverage points"],
    ),
    LensName.CRITICAL_THINKING: (
        "Evaluate whether claims and conclusions are well supported.",
        ["Identify main claim", "Identify assumptions", "Detect missing evidence"],
    ),
    LensName.CAUSAL_REASONING: (
        "Distinguish correlation from causation and test causal explanations.",
        ["Identify proposed cause", "Detect confounders", "Assess causal confidence"],
    ),
    LensName.DECISION_MAKING: (
        "Compare alternatives under uncertainty and trade-offs.",
        ["Define decision", "Identify constraints", "Compare scenarios"],
    ),
    LensName.PROBABILISTIC_THINKING: (
        "Reason explicitly about uncertainty.",
        ["Estimate probability", "Separate confidence from certainty", "Identify overconfidence"],
    ),
    LensName.FORECASTING: (
        "Reason about possible future states.",
        ["Define forecast target", "Decompose drivers", "Define update triggers"],
    ),
    LensName.SCIENTIFIC_REASONING: (
        "Test explanations against evidence.",
        ["Form hypothesis", "Define falsification condition", "Assess evidence quality"],
    ),
    LensName.PROBLEM_SOLVING: (
        "Turn an ambiguous problem into actionable structure.",
        ["Define problem", "Identify root causes", "Select minimum viable intervention"],
    ),
    LensName.ARGUMENTATION: (
        "Analyze structured disagreement.",
        ["Identify premises", "Identify conclusion", "Test premise sufficiency"],
    ),
    LensName.METACOGNITION_AND_BIAS: (
        "Challenge the quality of the reasoning process itself.",
        ["Detect confirmation bias", "Identify blind spots", "Calibrate confidence"],
    ),
}


def _selected_lenses(names: list[LensName]) -> list[SelectedLens]:
    return [
        SelectedLens(name=name, purpose=LENS_DEFINITIONS[name][0], operations=LENS_DEFINITIONS[name][1])
        for name in names
    ]


def build_mock_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """Build stable placeholder output without external services or randomness."""
    problem = request.problem.strip()
    confidence = Confidence(
        score=0.35,
        level="low",
        rationale="This mock analysis uses only the submitted problem and no supporting evidence.",
    )

    return AnalysisResponse(
        problem=problem,
        summary=f"A preliminary structural analysis of: {problem}",
        selected_lenses=_selected_lenses(request.selected_lenses),
        claims=[
            Claim(
                statement=f"The stated problem requires analysis: {problem}",
                evidence=["The problem statement supplied by the requester."],
                confidence=confidence,
            )
        ],
        assumptions=[
            Assumption(
                statement="The problem statement describes the relevant system boundary.",
                impact="An incomplete boundary could omit important actors or feedback effects.",
                validation_question="Which actors, time horizon, or constraints are outside the stated problem?",
            )
        ],
        unknowns=[
            Unknown(
                question="What evidence supports the problem statement?",
                importance="high",
            ),
            Unknown(
                question="What outcome would count as a meaningful improvement?",
                importance="high",
            ),
        ],
        leverage_points=[
            LeveragePoint(
                title="Clarify the system boundary",
                description="Identify the actors, constraints, and time horizon before choosing an intervention.",
                related_lens=LensName.SYSTEMS_THINKING,
                priority="high",
            )
        ],
        confidence=confidence,
        graph_nodes=[
            GraphNode(
                id="problem",
                label="Stated problem",
                category="problem",
                description=problem,
            ),
            GraphNode(
                id="evidence",
                label="Available evidence",
                category="evidence",
                description="Evidence needed to test the stated problem and its causes.",
            ),
            GraphNode(
                id="outcome",
                label="Desired outcome",
                category="outcome",
                description="A measurable improvement that has not yet been defined.",
            ),
        ],
        graph_edges=[
            GraphEdge(
                source="evidence",
                target="problem",
                relationship="tests",
                polarity="uncertain",
            ),
            GraphEdge(
                source="problem",
                target="outcome",
                relationship="motivates",
                polarity="positive",
            ),
        ],
    )
