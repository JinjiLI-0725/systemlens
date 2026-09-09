"""API and intelligence-layer tests."""

from fastapi.testclient import TestClient

from backend.main import app
from backend.reasoning.operations import (
    ACTIVE_OPERATIONS,
    CANON_OPERATION_IDS,
    INACTIVE_OPERATION_IDS,
    OPERATION_REGISTRY,
)
from backend.schemas.analysis import LensName
from backend.services.classifier import ProblemClass, classify_problem
from backend.services.lens_selector import select_lenses
from backend.services.planner import plan_operations

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_requested_examples_are_classified_transparently() -> None:
    assert (
        classify_problem("Why are young professionals leaving Hong Kong?")
        == ProblemClass.SYSTEM
    )
    assert (
        classify_problem("Should a startup hire now or wait six months?")
        == ProblemClass.DECISION
    )
    assert (
        classify_problem("Does remote work cause lower productivity?")
        == ProblemClass.CAUSAL
    )
    assert (
        classify_problem("This argument claims AI will replace all junior jobs.")
        == ProblemClass.ARGUMENT
    )


def test_automatic_lens_selection() -> None:
    assert select_lenses(ProblemClass.CAUSAL) == [
        LensName.CAUSAL_REASONING,
        LensName.CRITICAL_THINKING,
    ]


def test_explicit_selected_lenses_override_automatic_selection() -> None:
    response = client.post(
        "/analyze",
        json={
            "problem": "Should a startup hire now or wait six months?",
            "selected_lenses": ["systems_thinking"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert [lens["name"] for lens in body["selected_lenses"]] == ["systems_thinking"]
    assert body["execution_trace"]["selected_lenses"] == ["systems_thinking"]
    assert body["execution_trace"]["operations"] == [
        "define_system_boundary",
        "identify_stocks_and_flows",
        "detect_feedback_loops",
        "identify_leverage_points",
    ]


def test_operation_registry_is_machine_readable_and_bounded() -> None:
    assert len(ACTIVE_OPERATIONS) == 18
    assert len(OPERATION_REGISTRY) == len(ACTIVE_OPERATIONS)
    assert len(CANON_OPERATION_IDS) == 30
    assert OPERATION_REGISTRY["detect_confounders"].outputs == (
        "confounder",
        "pathway",
        "observed_or_unobserved",
        "severity",
    )


def test_every_active_operation_has_execution_metadata() -> None:
    for operation in ACTIVE_OPERATIONS:
        assert operation.source_basis
        assert operation.questions
        assert operation.outputs


def test_inactive_operations_cannot_be_scheduled() -> None:
    all_lenses = list(LensName)
    plan = plan_operations(all_lenses)
    assert set(plan) == set(OPERATION_REGISTRY)
    assert not (set(plan) & INACTIVE_OPERATION_IDS)


def test_planning_is_ordered_and_deterministic() -> None:
    lenses = [LensName.SYSTEMS_THINKING, LensName.CRITICAL_THINKING]
    expected = [
        "define_system_boundary",
        "identify_stocks_and_flows",
        "detect_feedback_loops",
        "identify_leverage_points",
        "identify_claim",
        "identify_assumptions",
        "detect_missing_evidence",
        "generate_counterarguments",
    ]
    assert plan_operations(lenses) == expected
    assert plan_operations(lenses) == expected


def test_analyze_returns_structured_deterministic_response_and_trace() -> None:
    request = {"problem": "Why are young professionals leaving Hong Kong?"}
    first_response = client.post("/analyze", json=request)
    second_response = client.post("/analyze", json=request)
    assert first_response.status_code == 200
    assert first_response.json() == second_response.json()

    body = first_response.json()
    assert body["problem"] == request["problem"]
    assert body["execution_trace"]["problem_class"] == "system_problem"
    assert body["execution_trace"]["selected_lenses"] == [
        "systems_thinking",
        "critical_thinking",
    ]
    assert body["execution_trace"]["operations"]
    assert "preliminary" in body["summary"].lower()
    for field in (
        "claims",
        "assumptions",
        "unknowns",
        "leverage_points",
        "graph_nodes",
        "graph_edges",
    ):
        assert body[field]


def test_confidence_is_lower_without_evidence_signals() -> None:
    unsupported = client.post(
        "/analyze", json={"problem": "Does remote work cause lower productivity?"}
    ).json()
    evidenced = client.post(
        "/analyze",
        json={
            "problem": "A study reports data from a measured sample: does remote work cause lower productivity?"
        },
    ).json()
    assert unsupported["confidence"]["score"] < evidenced["confidence"]["score"]
    assert unsupported["confidence"]["level"] == "low"
    assert "no explicit data" in unsupported["confidence"]["rationale"].lower()
    assert "unknowns remain" in unsupported["confidence"]["rationale"].lower()


def test_decision_and_argument_routes_do_not_use_every_lens() -> None:
    decision = client.post(
        "/analyze", json={"problem": "Should a startup hire now or wait six months?"}
    ).json()
    argument = client.post(
        "/analyze",
        json={"problem": "This argument claims AI will replace all junior jobs."},
    ).json()
    assert decision["execution_trace"]["problem_class"] == "decision_problem"
    assert "compare_alternatives" in decision["execution_trace"]["operations"]
    assert argument["execution_trace"]["problem_class"] == "argument_problem"
    assert len(argument["execution_trace"]["selected_lenses"]) == 2
