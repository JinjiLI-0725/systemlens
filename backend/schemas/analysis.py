"""Request and response contracts for structured SystemLens analysis."""

from enum import Enum

from pydantic import BaseModel, Field


class LensName(str, Enum):
    """Lenses defined by the SystemLens taxonomy."""

    SYSTEMS_THINKING = "systems_thinking"
    CRITICAL_THINKING = "critical_thinking"
    CAUSAL_REASONING = "causal_reasoning"
    DECISION_MAKING = "decision_making"
    PROBABILISTIC_THINKING = "probabilistic_thinking"
    FORECASTING = "forecasting"
    SCIENTIFIC_REASONING = "scientific_reasoning"
    PROBLEM_SOLVING = "problem_solving"
    ARGUMENTATION = "argumentation"
    METACOGNITION_AND_BIAS = "metacognition_and_bias"


class AnalysisRequest(BaseModel):
    """A problem and the taxonomy lenses through which to examine it."""

    problem: str = Field(min_length=1, max_length=10_000)
    selected_lenses: list[LensName] | None = Field(default=None, min_length=1)


class SelectedLens(BaseModel):
    """A selected lens and the taxonomy operations used in the analysis."""

    name: LensName
    purpose: str
    operations: list[str]


class Confidence(BaseModel):
    """A calibrated confidence assessment rather than a claim of certainty."""

    score: float = Field(ge=0, le=1)
    level: str
    rationale: str


class Claim(BaseModel):
    """A claim surfaced from the submitted problem."""

    statement: str
    evidence: list[str]
    confidence: Confidence


class Assumption(BaseModel):
    """An assumption whose validity affects the analysis."""

    statement: str
    impact: str
    validation_question: str


class Unknown(BaseModel):
    """Missing information that could materially change the analysis."""

    question: str
    importance: str


class LeveragePoint(BaseModel):
    """A place where an intervention may change system behavior."""

    title: str
    description: str
    related_lens: LensName
    priority: str


class GraphNode(BaseModel):
    """A variable, actor, driver, or outcome in the system graph."""

    id: str
    label: str
    category: str
    description: str


class GraphEdge(BaseModel):
    """A directed relationship between two graph nodes."""

    source: str
    target: str
    relationship: str
    polarity: str


class ExecutionTrace(BaseModel):
    """Inspectable execution metadata that never contains hidden reasoning."""

    problem_class: str
    selected_lenses: list[LensName]
    operations: list[str]
    execution_mode: str = "deterministic"
    requested_execution_mode: str = "deterministic"
    provider: str | None = None
    model: str | None = None
    batches: list[list[str]] = Field(default_factory=list)
    fallback_events: list[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    """The complete structured result returned by the analysis endpoint."""

    problem: str
    summary: str
    selected_lenses: list[SelectedLens]
    claims: list[Claim]
    assumptions: list[Assumption]
    unknowns: list[Unknown]
    leverage_points: list[LeveragePoint]
    confidence: Confidence
    graph_nodes: list[GraphNode]
    graph_edges: list[GraphEdge]
    execution_trace: ExecutionTrace
