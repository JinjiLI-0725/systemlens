"""Provider, batching, validation, fallback, and compatibility tests."""

import json

import httpx

from backend.llm.base import LLMProvider, LLMProviderError, Message
from backend.llm.config import ExecutionMode, LLMConfig, LLMProviderName
from backend.llm.deepseek import DeepSeekProvider
from backend.llm.openrouter import OpenRouterProvider
from backend.schemas.analysis import AnalysisRequest, AnalysisResponse
from backend.schemas.execution import BatchResult, OperationFinding
from backend.services.analysis import build_analysis
from backend.services.executor import batch_operations, build_batch_messages


def _finding(operation_id: str) -> OperationFinding:
    return OperationFinding(
        operation_id=operation_id,
        observations=["Only the prompt was observed."],
        inferences=["A candidate relationship may exist."],
        assumptions=["The framing is representative."],
        unknowns=["What evidence tests the relationship?"],
        conclusions=[f"Preliminary conclusion for {operation_id}."],
        confidence=0.42,
    )


class FakeProvider(LLMProvider):
    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.calls: list[list[Message]] = []

    @property
    def name(self) -> str:
        return "fake"

    @property
    def model(self) -> str:
        return "fake-structured"

    def generate_structured(self, messages, response_model):
        self.calls.append(messages)
        if len(self.calls) <= self.failures:
            raise LLMProviderError("invalid JSON")
        prompt = messages[1].content
        operation_ids = [
            operation_id
            for operation_id in (
                "define_system_boundary",
                "identify_stocks_and_flows",
                "detect_feedback_loops",
                "identify_leverage_points",
                "identify_claim",
                "identify_assumptions",
                "detect_missing_evidence",
                "generate_counterarguments",
            )
            if f'"id": "{operation_id}"' in prompt
        ]
        return response_model(findings=[_finding(item) for item in operation_ids])


def test_provider_abstraction_is_implemented() -> None:
    assert issubclass(DeepSeekProvider, LLMProvider)
    assert issubclass(OpenRouterProvider, LLMProvider)


def test_environment_configuration_and_missing_key(monkeypatch) -> None:
    monkeypatch.setenv("SYSTEMLENS_EXECUTION_MODE", "llm")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-reasoner")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    config = LLMConfig.from_env()
    assert config.execution_mode is ExecutionMode.LLM
    assert config.effective_mode is ExecutionMode.DETERMINISTIC
    assert config.deepseek_model == "deepseek-reasoner"


def test_deepseek_openai_compatible_request_construction() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["authorization"] = request.headers["authorization"]
        captured["body"] = json.loads(request.content)
        content = BatchResult(findings=[_finding("identify_claim")]).model_dump_json()
        return httpx.Response(
            200, json={"choices": [{"message": {"content": content}}]}
        )

    provider = DeepSeekProvider(
        "secret",
        model="test-model",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = provider.generate_structured(
        [Message(role="user", content="test")], BatchResult
    )
    assert result.findings[0].operation_id == "identify_claim"
    assert captured["authorization"] == "Bearer secret"
    assert captured["body"]["response_format"] == {"type": "json_object"}
    assert captured["body"]["temperature"] == 0.2


def test_openrouter_environment_configuration(monkeypatch) -> None:
    monkeypatch.setenv("SYSTEMLENS_EXECUTION_MODE", "llm")
    monkeypatch.setenv("SYSTEMLENS_LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "not-logged")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://router.example/v1/")
    monkeypatch.setenv("OPENROUTER_MODEL", "deepseek/custom-model")
    config = LLMConfig.from_env()
    assert config.provider is LLMProviderName.OPENROUTER
    assert config.effective_mode is ExecutionMode.LLM
    assert config.openrouter_base_url == "https://router.example/v1/"
    assert config.openrouter_model == "deepseek/custom-model"


def test_openrouter_request_and_structured_response() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers["authorization"]
        captured["body"] = json.loads(request.content)
        content = BatchResult(findings=[_finding("identify_claim")]).model_dump_json()
        return httpx.Response(
            200, json={"choices": [{"message": {"content": content}}]}
        )

    provider = OpenRouterProvider(
        "secret",
        model="deepseek/selected-model",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = provider.generate_structured(
        [Message(role="user", content="test")], BatchResult
    )
    assert result.findings[0].operation_id == "identify_claim"
    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert captured["authorization"] == "Bearer secret"
    assert captured["body"]["model"] == "deepseek/selected-model"
    assert captured["body"]["response_format"] == {"type": "json_object"}


def test_openrouter_invalid_structured_response_raises_provider_error() -> None:
    provider = OpenRouterProvider(
        "secret",
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200, json={"choices": [{"message": {"content": "not-json"}}]}
                )
            )
        ),
    )
    try:
        provider.generate_structured([Message(role="user", content="test")], BatchResult)
    except LLMProviderError:
        pass
    else:
        raise AssertionError("invalid OpenRouter output should fail validation")


def test_openrouter_provider_selection_and_trace(monkeypatch) -> None:
    selected = FakeProvider()
    selected._name = "openrouter"
    selected._model = "deepseek/selected-model"
    monkeypatch.setattr(
        "backend.services.analysis.OpenRouterProvider", lambda **kwargs: selected
    )
    monkeypatch.setattr(
        FakeProvider, "name", property(lambda self: getattr(self, "_name", "fake"))
    )
    monkeypatch.setattr(
        FakeProvider,
        "model",
        property(lambda self: getattr(self, "_model", "fake-structured")),
    )
    response = build_analysis(
        AnalysisRequest(problem="Why are young professionals leaving Hong Kong?"),
        LLMConfig(
            execution_mode=ExecutionMode.LLM,
            provider=LLMProviderName.OPENROUTER,
            openrouter_api_key="secret",
            openrouter_model="deepseek/selected-model",
        ),
    )
    assert len(selected.calls) == 2
    assert response.execution_trace.provider == "openrouter"
    assert response.execution_trace.model == "deepseek/selected-model"
    assert response.execution_trace.execution_mode == "llm"
    assert response.execution_trace.batches
    assert response.execution_trace.fallback_events == []


def test_missing_openrouter_key_uses_deterministic_fallback() -> None:
    response = build_analysis(
        AnalysisRequest(problem="Does remote work cause lower productivity?"),
        LLMConfig(
            execution_mode=ExecutionMode.LLM,
            provider=LLMProviderName.OPENROUTER,
            deepseek_api_key="irrelevant-key",
        ),
    )
    assert response.execution_trace.execution_mode == "deterministic"
    assert response.execution_trace.provider is None
    assert response.execution_trace.fallback_events


def test_openrouter_failure_falls_back_per_batch() -> None:
    provider = OpenRouterProvider(
        "secret",
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(503, json={"error": "unavailable"})
            )
        ),
    )
    response = build_analysis(
        AnalysisRequest(problem="Why are young professionals leaving Hong Kong?"),
        LLMConfig(execution_mode=ExecutionMode.LLM, deepseek_api_key="enabled"),
        provider,
    )
    assert response.execution_trace.provider == "openrouter"
    assert response.execution_trace.execution_mode == "llm"
    assert len(response.execution_trace.fallback_events) == 2
    assert all(
        "deterministic fallback" in event
        for event in response.execution_trace.fallback_events
    )


def test_batches_follow_operation_families_and_prompt_uses_metadata() -> None:
    operations = [
        "define_system_boundary",
        "identify_stocks_and_flows",
        "identify_claim",
        "identify_assumptions",
    ]
    batches = batch_operations(operations)
    assert [item.operations for item in batches] == [operations[:2], operations[2:]]
    prompt = build_batch_messages("A problem", batches[0])
    assert "purpose" in prompt[1].content
    assert "source_basis" in prompt[1].content
    assert "Never fabricate" in prompt[0].content
    assert "chain-of-thought" in prompt[0].content


def test_successful_llm_execution_and_trace_metadata() -> None:
    provider = FakeProvider()
    response = build_analysis(
        AnalysisRequest(problem="Why are young professionals leaving Hong Kong?"),
        LLMConfig(execution_mode=ExecutionMode.LLM, deepseek_api_key="test"),
        provider,
    )
    assert response.execution_trace.execution_mode == "llm"
    assert response.execution_trace.provider == "fake"
    assert response.execution_trace.model == "fake-structured"
    assert len(provider.calls) == 2
    assert "Preliminary conclusion" in response.summary


def test_invalid_json_is_repaired_once() -> None:
    provider = FakeProvider(failures=1)
    response = build_analysis(
        AnalysisRequest(problem="Why are young professionals leaving Hong Kong?"),
        LLMConfig(execution_mode=ExecutionMode.LLM, deepseek_api_key="test"),
        provider,
    )
    assert len(provider.calls) == 3
    assert "Repair the previous answer" in provider.calls[1][-1].content
    assert response.execution_trace.fallback_events == []


def test_second_invalid_response_falls_back_for_batch() -> None:
    provider = FakeProvider(failures=2)
    response = build_analysis(
        AnalysisRequest(problem="Why are young professionals leaving Hong Kong?"),
        LLMConfig(execution_mode=ExecutionMode.LLM, deepseek_api_key="test"),
        provider,
    )
    assert len(response.execution_trace.fallback_events) == 1
    assert "deterministic fallback" in response.execution_trace.fallback_events[0]


def test_no_api_key_uses_deterministic_output_without_provider_call() -> None:
    provider = FakeProvider()
    response = build_analysis(
        AnalysisRequest(problem="Does remote work cause lower productivity?"),
        LLMConfig(execution_mode=ExecutionMode.LLM),
        provider,
    )
    assert response.execution_trace.execution_mode == "deterministic"
    assert provider.calls == []
    assert response.execution_trace.fallback_events


def test_public_analysis_response_remains_valid() -> None:
    response = build_analysis(AnalysisRequest(problem="A complex situation"))
    reparsed = AnalysisResponse.model_validate(response.model_dump())
    assert reparsed.problem == "A complex situation"
    assert reparsed.claims and reparsed.graph_nodes and reparsed.graph_edges
