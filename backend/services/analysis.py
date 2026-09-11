"""Orchestration, execution, and synthesis for SystemLens."""

import re

from backend.llm.base import LLMProvider
from backend.llm.config import ExecutionMode, LLMConfig, LLMProviderName
from backend.llm.deepseek import DeepSeekProvider
from backend.llm.openrouter import OpenRouterProvider
from backend.reasoning.operations import LENS_PURPOSES, operations_for_lens
from backend.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    Assumption,
    Claim,
    CompetingExplanation,
    Confidence,
    ExecutionTrace,
    GraphEdge,
    GraphNode,
    KeyDriver,
    LeveragePoint,
    LensName,
    NextCheck,
    SelectedLens,
    Unknown,
)
from backend.schemas.execution import BatchResult, OperationFinding
from backend.services.classifier import ProblemClass, classify_problem
from backend.services.executor import batch_operations, execute_batches
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

ALTERNATIVE_OPERATION_IDS = {
    "generate_counterarguments",
    "detect_confounders",
    "test_reverse_causation",
    "generate_counterfactual",
}

DRIVER_OPERATION_IDS = {
    "identify_stocks_and_flows",
    "detect_feedback_loops",
    "identify_leverage_points",
    "detect_confounders",
    "test_reverse_causation",
}


def _subject(problem: str) -> str:
    return problem.rstrip(" ?.!")


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item.strip() for item in items if item and item.strip()))


def _compact_title(text: str, limit: int = 72) -> str:
    clean = " ".join(text.split())
    for separator in (":", ";", " — ", " - "):
        if separator in clean:
            head = clean.split(separator, 1)[0].strip()
            if 8 <= len(head) <= limit:
                return head
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def _finding_text(findings: list[OperationFinding], operation_ids: set[str]) -> list[str]:
    selected = [item for item in findings if item.operation_id in operation_ids]
    return _unique(
        [text for item in selected for text in item.inferences]
        + [text for item in selected for text in item.conclusions]
    )


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


def _build_deterministic_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """Run classification, lens selection, planning, and conservative template execution."""
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

    diagnosis = (
        f"This appears to be a {problem_class.value.replace('_', ' ')} question, but the prompt alone "
        "does not establish which explanation is strongest. Treat the analysis below as a map of "
        "candidate mechanisms and tests rather than a factual verdict."
    )

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
        GraphEdge(source="boundary", target="actors", relationship="scopes", polarity="uncertain"),
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
    if "identify_stocks_and_flows" in plan:
        graph_edges.append(
            GraphEdge(
                source="drivers",
                target="outcome",
                relationship="candidate inflow or outflow affecting an accumulation",
                polarity="uncertain",
            )
        )
    if "distinguish_correlation_from_causation" in plan:
        graph_edges.append(
            GraphEdge(
                source="drivers",
                target="outcome",
                relationship="observed association; causal direction not established",
                polarity="uncertain",
            )
        )

    return AnalysisResponse(
        problem=problem,
        diagnosis=diagnosis,
        key_drivers=[],
        competing_explanations=[],
        next_checks=[
            NextCheck(
                question=item.question,
                signal="Evidence here could materially strengthen, weaken, or redirect the diagnosis.",
            )
            for item in unknowns[:5]
        ],
        synthesis=diagnosis,
        summary=diagnosis,
        selected_lenses=_selected_lens_details(lenses),
        claims=[
            Claim(
                statement=f"Preliminary claim under examination: {_subject(problem)}.",
                evidence=["The submitted wording is the only direct input; it is not corroborating evidence."],
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


def _synthesize_llm_analysis(
    baseline: AnalysisResponse, results: list[BatchResult]
) -> AnalysisResponse:
    """Turn validated operation findings into an insight-first public response."""
    findings = [finding for result in results for finding in result.findings]
    conclusions = _unique([text for finding in findings for text in finding.conclusions])
    assumptions = _unique([text for finding in findings for text in finding.assumptions])
    unknowns = _unique([text for finding in findings for text in finding.unknowns])
    observations = _unique([text for finding in findings for text in finding.observations])
    inferences = _unique([text for finding in findings for text in finding.inferences])

    average = (
        round(sum(item.confidence for item in findings) / len(findings), 2)
        if findings
        else baseline.confidence.score
    )
    confidence = Confidence(
        score=average,
        level="high" if average >= 0.75 else "moderate" if average >= 0.5 else "low",
        rationale=(
            "Calibrated from validated batch outputs; the diagnosis remains preliminary and "
            "source evidence has not been independently verified."
        ),
    )

    diagnosis_parts = conclusions[:2]
    diagnosis = " ".join(diagnosis_parts) if diagnosis_parts else baseline.diagnosis
    synthesis = " ".join(conclusions[:6]) or baseline.synthesis

    driver_texts = _finding_text(findings, DRIVER_OPERATION_IDS)
    if not driver_texts:
        driver_texts = _unique(inferences + conclusions)
    key_drivers = [
        KeyDriver(title=_compact_title(item), explanation=item)
        for item in driver_texts[:6]
    ]

    alternative_texts = _finding_text(findings, ALTERNATIVE_OPERATION_IDS)
    competing_explanations = [
        CompetingExplanation(
            explanation=item,
            why_it_matters="If this explanation fits the evidence better, the leading diagnosis or intervention should change.",
        )
        for item in alternative_texts[:5]
    ]

    next_checks = [
        NextCheck(
            question=item,
            signal="Look for evidence that discriminates between the leading diagnosis and plausible alternatives.",
        )
        for item in unknowns[:6]
    ] or baseline.next_checks

    leverage_texts = _finding_text(findings, {"identify_leverage_points"})
    leverage_points = [
        LeveragePoint(
            title=_compact_title(item),
            description=item,
            related_lens=LensName.SYSTEMS_THINKING,
            priority="high" if index == 0 else "medium",
        )
        for index, item in enumerate(leverage_texts[:4])
    ] or baseline.leverage_points

    payload = baseline.model_dump()
    payload.update(
        {
            "diagnosis": diagnosis,
            "key_drivers": key_drivers,
            "competing_explanations": competing_explanations,
            "next_checks": next_checks,
            "synthesis": synthesis,
            "summary": diagnosis,
            "claims": [
                Claim(statement=item, evidence=observations[:3], confidence=confidence)
                for item in conclusions[:6]
            ]
            or baseline.claims,
            "assumptions": [
                Assumption(
                    statement=f"Preliminary hypothesis: {item}",
                    impact="If false, one or more parts of the diagnosis may change.",
                    validation_question="What observation would verify or falsify this assumption?",
                )
                for item in assumptions
            ][:8]
            or baseline.assumptions,
            "unknowns": [Unknown(question=item, importance="high") for item in unknowns][:8]
            or baseline.unknowns,
            "leverage_points": leverage_points,
            "confidence": confidence,
        }
    )
    return AnalysisResponse.model_validate(payload)


def build_analysis(
    request: AnalysisRequest,
    config: LLMConfig | None = None,
    provider: LLMProvider | None = None,
) -> AnalysisResponse:
    """Run the pipeline with optional provider-backed batch execution."""
    settings = config or LLMConfig.from_env()
    baseline = _build_deterministic_analysis(request)
    batches = batch_operations(
        baseline.execution_trace.operations, maximum_size=settings.batch_size
    )
    trace_updates = {
        "requested_execution_mode": settings.execution_mode.value,
        "execution_mode": settings.effective_mode.value,
        "batches": [batch.operations for batch in batches],
    }
    if settings.effective_mode is ExecutionMode.DETERMINISTIC:
        if settings.execution_mode is ExecutionMode.LLM:
            trace_updates["fallback_events"] = [
                "LLM execution requested without an API key; deterministic execution used."
            ]
        return baseline.model_copy(
            update={
                "execution_trace": baseline.execution_trace.model_copy(update=trace_updates)
            }
        )

    if provider is not None:
        active_provider = provider
    elif settings.provider is LLMProviderName.OPENROUTER:
        active_provider = OpenRouterProvider(
            api_key=settings.openrouter_api_key or "",
            model=settings.openrouter_model,
            base_url=settings.openrouter_base_url,
            timeout=settings.timeout_seconds,
            max_output_tokens=settings.max_output_tokens,
        )
    else:
        active_provider = DeepSeekProvider(
            api_key=settings.deepseek_api_key or "",
            model=settings.deepseek_model,
            base_url=settings.deepseek_base_url,
            timeout=settings.timeout_seconds,
            max_output_tokens=settings.max_output_tokens,
        )
    execution = execute_batches(
        request.problem.strip(),
        batches,
        active_provider,
        request_timeout=settings.request_timeout_seconds,
    )
    response = _synthesize_llm_analysis(baseline, execution.results)
    trace_updates.update(
        {
            "provider": active_provider.name,
            "model": active_provider.model,
            "fallback_events": execution.fallbacks,
            "batch_timings": execution.timings,
        }
    )
    return response.model_copy(
        update={
            "execution_trace": baseline.execution_trace.model_copy(update=trace_updates)
        }
    )


# Compatibility for internal callers that used the v0 mock function name.
build_mock_analysis = _build_deterministic_analysis
