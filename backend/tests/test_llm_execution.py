"""Provider, batching, validation, fallback, and compatibility tests."""

import json
import threading
import time

import httpx

from backend.llm.base import LLMProvider, LLMProviderError, Message
from backend.llm.config import ExecutionMode, LLMConfig, LLMProviderName
from backend.llm.deepseek import DeepSeekProvider
from backend.llm.openrouter import OpenRouterProvider
from backend.schemas.analysis import AnalysisRequest, AnalysisResponse
from backend.schemas.execution import BatchResult, ExecutionBatch, OperationFinding
from backend.services.analysis import build_analysis
from backend.services.executor import (
    batch_operations,
    build_batch_messages,
    execute_batches,
)


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
            raise LLMProviderError("invalid JSON", "parsing_error")
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
            if f'"id":"{operation_id}"' in prompt
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
    except LLMProviderError as exc:
        assert exc.category == "parsing_error"
    else:
        raise AssertionError("invalid OpenRouter output should fail validation")


def test_openrouter_schema_error_is_distinct_from_invalid_json() -> None:
    provider = OpenRouterProvider(
        "secret",
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={
                        "choices": [
                            {
                                "message": {
                                    "content": '{"findings":[{"operation_id":"identify_claim"}]}'
                                }
                            }
                        ]
                    },
                )
            )
        ),
    )
    try:
        provider.generate_structured([Message(role="user", content="test")], BatchResult)
    except LLMProviderError as exc:
        assert exc.category == "schema_error"
    else:
        raise AssertionError("schema-invalid OpenRouter output should fail validation")


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
    assert len(selected.calls) == 4
    assert response.execution_trace.provider == "openrouter"
    assert response.execution_trace.model == "deepseek/selected-model"
    assert response.execution_trace.execution_mode == "llm"
    assert response.execution_trace.batches
    assert len(response.execution_trace.batch_timings) == 4
    assert not any(item.fallback_used for item in response.execution_trace.batch_timings)
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
    assert len(response.execution_trace.fallback_events) == 4
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
    assert '"purpose"' in prompt[1].content
    assert '"questions"' in prompt[1].content
    assert '"outputs"' in prompt[1].content
    assert "findings array length MUST equal 2" in prompt[1].content
    assert "Copy each supplied operation_id verbatim" in prompt[1].content
    assert '"operation_id":"define_system_boundary"' in prompt[1].content
    assert "Never fabricate" in prompt[0].content
    assert "chain-of-thought" in prompt[0].content


def test_default_and_configurable_batch_size(monkeypatch) -> None:
    operations = [
        "define_system_boundary",
        "identify_stocks_and_flows",
        "detect_feedback_loops",
        "identify_leverage_points",
    ]
    assert [len(batch.operations) for batch in batch_operations(operations)] == [2, 2]
    monkeypatch.setenv("SYSTEMLENS_BATCH_SIZE", "3")
    config = LLMConfig.from_env()
    assert config.batch_size == 3
    assert [len(batch.operations) for batch in batch_operations(
        operations, config.batch_size
    )] == [3, 1]


def test_latency_limits_are_configurable(monkeypatch) -> None:
    monkeypatch.setenv("SYSTEMLENS_LLM_TIMEOUT", "7.5")
    monkeypatch.setenv("SYSTEMLENS_MAX_OUTPUT_TOKENS", "640")
    monkeypatch.setenv("SYSTEMLENS_REQUEST_TIMEOUT", "9")
    config = LLMConfig.from_env()
    assert config.timeout_seconds == 7.5
    assert config.max_output_tokens == 640
    assert config.request_timeout_seconds == 9
    provider = OpenRouterProvider("secret", max_output_tokens=config.max_output_tokens)
    assert provider.build_request([Message(role="user", content="test")])["max_tokens"] == 640


def test_openrouter_timeout_is_wrapped_as_provider_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("too slow", request=request)

    provider = OpenRouterProvider(
        "secret", client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    try:
        provider.generate_structured([Message(role="user", content="test")], BatchResult)
    except LLMProviderError:
        pass
    else:
        raise AssertionError("provider timeout should be normalized")


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
    assert len(provider.calls) == 4
    assert "Preliminary conclusion" in response.summary


def test_invalid_json_does_not_trigger_full_model_retry() -> None:
    provider = FakeProvider(failures=1)
    response = build_analysis(
        AnalysisRequest(problem="Why are young professionals leaving Hong Kong?"),
        LLMConfig(execution_mode=ExecutionMode.LLM, deepseek_api_key="test"),
        provider,
    )
    assert len(provider.calls) == 4
    assert not any(
        "Repair the previous answer" in call[-1].content for call in provider.calls
    )
    assert len(response.execution_trace.fallback_events) == 1


class StaticProvider(LLMProvider):
    def __init__(
        self,
        result: BatchResult | None = None,
        error: LLMProviderError | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.calls = 0

    @property
    def name(self) -> str:
        return "static"

    @property
    def model(self) -> str:
        return "mock"

    def generate_structured(self, messages, response_model):
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


def _two_operation_batch() -> ExecutionBatch:
    return ExecutionBatch(
        name="critical_thinking",
        operations=["identify_claim", "identify_assumptions"],
    )


def test_fully_valid_batch_has_llm_status() -> None:
    provider = StaticProvider(
        BatchResult(
            findings=[_finding("identify_claim"), _finding("identify_assumptions")]
        )
    )
    execution = execute_batches("problem", [_two_operation_batch()], provider)
    assert provider.calls == 1
    assert execution.timings[0].status == "llm"
    assert execution.timings[0].validation_error_category is None
    assert execution.fallbacks == []


def test_missing_operation_is_filled_without_replacing_valid_finding() -> None:
    provider = StaticProvider(BatchResult(findings=[_finding("identify_claim")]))
    execution = execute_batches("problem", [_two_operation_batch()], provider)
    assert provider.calls == 1
    assert execution.timings[0].status == "partial_fallback"
    assert execution.timings[0].missing_operation_ids == ["identify_assumptions"]
    assert execution.timings[0].validation_error_category == "coverage_error"
    assert execution.results[0].findings[0].confidence == 0.42
    assert execution.results[0].findings[1].confidence == 0.3


def test_extra_operation_is_discarded_and_order_is_stable() -> None:
    provider = StaticProvider(
        BatchResult(
            findings=[
                _finding("identify_assumptions"),
                _finding("generate_counterarguments"),
                _finding("identify_claim"),
            ]
        )
    )
    execution = execute_batches("problem", [_two_operation_batch()], provider)
    assert execution.timings[0].status == "partial_fallback"
    assert execution.timings[0].missing_operation_ids == []
    assert [item.operation_id for item in execution.results[0].findings] == [
        "identify_claim",
        "identify_assumptions",
    ]
    assert all(item.confidence == 0.42 for item in execution.results[0].findings)


def test_only_extra_operations_require_full_deterministic_fallback() -> None:
    provider = StaticProvider(
        BatchResult(findings=[_finding("generate_counterarguments")])
    )
    execution = execute_batches("problem", [_two_operation_batch()], provider)
    assert execution.timings[0].status == "deterministic_fallback"
    assert execution.timings[0].missing_operation_ids == _two_operation_batch().operations
    assert all(item.confidence == 0.3 for item in execution.results[0].findings)


def test_duplicate_operation_keeps_first_valid_instance() -> None:
    first = _finding("identify_claim")
    first.confidence = 0.71
    duplicate = _finding("identify_claim")
    duplicate.confidence = 0.12
    provider = StaticProvider(
        BatchResult(findings=[first, duplicate, _finding("identify_assumptions")])
    )
    execution = execute_batches("problem", [_two_operation_batch()], provider)
    assert execution.timings[0].status == "partial_fallback"
    assert execution.results[0].findings[0].confidence == 0.71
    assert execution.results[0].findings[1].confidence == 0.42


def test_invalid_json_category_is_safe_and_deterministic() -> None:
    raw_output = "RAW_MODEL_SECRET_PAYLOAD"
    api_key = "API_KEY_MUST_NOT_LEAK"
    provider = StaticProvider(
        error=LLMProviderError(f"invalid JSON: {raw_output} {api_key}", "parsing_error")
    )
    execution = execute_batches("problem", [_two_operation_batch()], provider)
    timing = execution.timings[0]
    assert provider.calls == 1
    assert timing.status == "deterministic_fallback"
    assert timing.missing_operation_ids == _two_operation_batch().operations
    assert timing.validation_error_category == "parsing_error"
    trace_text = json.dumps(
        {"timing": timing.model_dump(), "fallbacks": execution.fallbacks}
    )
    assert raw_output not in trace_text
    assert api_key not in trace_text


class DelayedProvider(FakeProvider):
    def __init__(self, delays: dict[str, float], failing: set[str] | None = None) -> None:
        super().__init__()
        self.delays = delays
        self.failing = failing or set()
        self.active = 0
        self.maximum_active = 0
        self.lock = threading.Lock()

    def generate_structured(self, messages, response_model):
        operation_id = next(
            item for item in self.delays if f'"id":"{item}"' in messages[1].content
        )
        with self.lock:
            self.active += 1
            self.maximum_active = max(self.maximum_active, self.active)
        try:
            time.sleep(self.delays[operation_id])
            if operation_id in self.failing:
                raise LLMProviderError("mock failure")
            return response_model(findings=[_finding(operation_id)])
        finally:
            with self.lock:
                self.active -= 1


def test_batches_run_in_parallel_and_results_keep_plan_order() -> None:
    first = ExecutionBatch(name="systems_thinking", operations=["define_system_boundary"])
    second = ExecutionBatch(name="critical_thinking", operations=["identify_claim"])
    provider = DelayedProvider({"define_system_boundary": 0.08, "identify_claim": 0.01})
    execution = execute_batches("problem", [first, second], provider, request_timeout=1)
    assert provider.maximum_active == 2
    assert [result.findings[0].operation_id for result in execution.results] == [
        "define_system_boundary",
        "identify_claim",
    ]
    assert [timing.batch_name for timing in execution.timings] == [
        "systems_thinking",
        "critical_thinking",
    ]


def test_partial_failure_falls_back_without_discarding_other_batch() -> None:
    batches = [
        ExecutionBatch(name="systems_thinking", operations=["define_system_boundary"]),
        ExecutionBatch(name="critical_thinking", operations=["identify_claim"]),
    ]
    provider = DelayedProvider(
        {"define_system_boundary": 0, "identify_claim": 0},
        failing={"identify_claim"},
    )
    execution = execute_batches("problem", batches, provider, request_timeout=1)
    assert [item.fallback_used for item in execution.timings] == [False, True]
    assert len(execution.fallbacks) == 1
    assert execution.results[0].findings[0].confidence == 0.42
    assert execution.results[1].findings[0].confidence == 0.3


def test_global_request_budget_falls_back_for_unfinished_batches() -> None:
    batches = [
        ExecutionBatch(name="systems_thinking", operations=["define_system_boundary"]),
        ExecutionBatch(name="critical_thinking", operations=["identify_claim"]),
    ]
    provider = DelayedProvider({"define_system_boundary": 0, "identify_claim": 0.15})
    started = time.monotonic()
    execution = execute_batches("problem", batches, provider, request_timeout=0.03)
    assert time.monotonic() - started < 0.12
    assert [item.fallback_used for item in execution.timings] == [False, True]
    assert "global request time budget" in execution.fallbacks[0]
    assert execution.results[1].findings[0].confidence == 0.3


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
