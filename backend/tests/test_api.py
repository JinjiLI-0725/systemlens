"""API contract tests."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_returns_structured_deterministic_response() -> None:
    request = {
        "problem": "Customer wait times are increasing",
        "selected_lenses": ["systems_thinking", "causal_reasoning"],
    }

    first_response = client.post("/analyze", json=request)
    second_response = client.post("/analyze", json=request)

    assert first_response.status_code == 200
    assert first_response.json() == second_response.json()

    body = first_response.json()
    assert body["problem"] == request["problem"]
    assert [lens["name"] for lens in body["selected_lenses"]] == request["selected_lenses"]
    assert body["claims"]
    assert body["assumptions"]
    assert body["unknowns"]
    assert body["leverage_points"]
    assert body["confidence"]["score"] == 0.35
    assert body["graph_nodes"]
    assert body["graph_edges"]
