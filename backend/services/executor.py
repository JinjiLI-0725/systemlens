"""Provider-neutral batched operation execution."""

import json
import time
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field

from backend.llm.base import LLMProvider, LLMProviderError, Message
from backend.reasoning.operations import OPERATION_REGISTRY
from backend.schemas.execution import (
    BatchResult,
    BatchTiming,
    ExecutionBatch,
    OperationFinding,
)


def batch_operations(
    operation_ids: list[str], maximum_size: int = 2
) -> list[ExecutionBatch]:
    """Group adjacent operations by canonical family and cap batch size."""
    batches: list[ExecutionBatch] = []
    current_family = ""
    current: list[str] = []
    for operation_id in operation_ids:
        family = OPERATION_REGISTRY[operation_id].family
        if current and (family != current_family or len(current) >= maximum_size):
            batches.append(ExecutionBatch(name=current_family, operations=current))
            current = []
        current_family = family
        current.append(operation_id)
    if current:
        batches.append(ExecutionBatch(name=current_family, operations=current))
    return batches


def build_batch_messages(problem: str, batch: ExecutionBatch) -> list[Message]:
    """Construct an evidence-safe prompt directly from registry metadata."""
    metadata = []
    for item in batch.operations:
        operation = OPERATION_REGISTRY[item]
        metadata.append(
            {
                "id": operation.id,
                "purpose": operation.purpose,
                "questions": operation.questions,
                "outputs": operation.outputs,
            }
        )
    example = {
        "findings": [
            {
                "operation_id": operation_id,
                "observations": ["concise observation"],
                "inferences": ["concise inference"],
                "assumptions": ["concise assumption"],
                "unknowns": ["concise unknown"],
                "conclusions": ["concise conclusion"],
                "confidence": 0.5,
            }
            for operation_id in batch.operations
        ]
    }
    system = (
        "You execute analytical operations and return JSON only. Treat every output as a "
        "preliminary hypothesis unless supported by the input. Separate observations from "
        "inferences and preserve uncertainty. Never fabricate evidence or reveal chain-of-thought."
    )
    user = (
        f"Problem:\n{problem}\n\nOperations metadata:\n"
        f"{json.dumps(metadata, separators=(',', ':'))}\n\n"
        f"Return JSON matching this exact template:\n{json.dumps(example, separators=(',', ':'))}\n"
        f"The findings array length MUST equal {len(batch.operations)}. Copy each supplied "
        "operation_id verbatim, exactly once. Keep every text array concise. Confidence is 0 to 1."
    )
    return [Message(role="system", content=system), Message(role="user", content=user)]


def deterministic_batch(batch: ExecutionBatch) -> BatchResult:
    """Produce conservative per-operation placeholders for local fallback."""
    return BatchResult(
        findings=[
            OperationFinding(
                operation_id=operation_id,
                observations=[
                    "The submitted problem statement is the only direct observation."
                ],
                inferences=[],
                assumptions=["The problem framing may be incomplete or contested."],
                unknowns=list(OPERATION_REGISTRY[operation_id].questions[:2]),
                conclusions=[
                    f"{OPERATION_REGISTRY[operation_id].name} remains a preliminary analytical hypothesis."
                ],
                confidence=0.3,
            )
            for operation_id in batch.operations
        ]
    )


@dataclass
class BatchExecution:
    """Results and safe trace details from all operation batches."""

    results: list[BatchResult] = field(default_factory=list)
    fallbacks: list[str] = field(default_factory=list)
    timings: list[BatchTiming] = field(default_factory=list)


def execute_batches(
    problem: str,
    batches: list[ExecutionBatch],
    provider: LLMProvider,
    request_timeout: float = 30.0,
) -> BatchExecution:
    """Execute independent batches concurrently within one global time budget."""
    execution = BatchExecution()
    if not batches:
        return execution

    pool = ThreadPoolExecutor(max_workers=len(batches), thread_name_prefix="llm-batch")
    started = time.monotonic()
    futures: list[Future[tuple[BatchResult, BatchTiming, str | None]]] = [
        pool.submit(_execute_batch, problem, batch, provider) for batch in batches
    ]
    done, _ = wait(futures, timeout=request_timeout)
    budget_elapsed_ms = round((time.monotonic() - started) * 1000)

    # Read futures in plan order rather than completion order so synthesis is stable.
    for batch, future in zip(batches, futures):
        if future in done:
            result, timing, event = future.result()
        else:
            future.cancel()
            event = (
                f"Batch '{batch.name}' exceeded the global request time budget; "
                "deterministic fallback used."
            )
            result = deterministic_batch(batch)
            timing = BatchTiming(
                batch_name=batch.name,
                elapsed_ms=budget_elapsed_ms,
                fallback_used=True,
                status="deterministic_fallback",
                missing_operation_ids=batch.operations,
                validation_error_category="request_timeout",
            )
        execution.results.append(_restrict_findings(result, batch))
        execution.timings.append(timing)
        if event:
            execution.fallbacks.append(event)
    pool.shutdown(wait=False, cancel_futures=True)
    return execution


def _execute_batch(
    problem: str, batch: ExecutionBatch, provider: LLMProvider
) -> tuple[BatchResult, BatchTiming, str | None]:
    """Execute one batch and salvage valid findings without another model call."""
    started = time.monotonic()
    messages = build_batch_messages(problem, batch)
    try:
        result = provider.generate_structured(messages, BatchResult)
        result, status, missing = _reconcile_batch_result(result, batch)
        category = None if status == "llm" else "coverage_error"
        event = None
        if status != "llm":
            event = (
                f"Batch '{batch.name}' had a safe coverage validation failure; "
                f"{status.replace('_', ' ')} used."
            )
    except LLMProviderError as exc:
        result = deterministic_batch(batch)
        status = "deterministic_fallback"
        missing = list(batch.operations)
        category = exc.category
        event = (
            f"Batch '{batch.name}' had a safe {category}; deterministic fallback used."
        )
    elapsed_ms = round((time.monotonic() - started) * 1000)
    timing = BatchTiming(
        batch_name=batch.name,
        elapsed_ms=elapsed_ms,
        fallback_used=status != "llm",
        status=status,
        missing_operation_ids=missing,
        validation_error_category=category,
    )
    return result, timing, event


def _reconcile_batch_result(
    result: BatchResult, batch: ExecutionBatch
) -> tuple[BatchResult, str, list[str]]:
    """Keep the first usable finding and deterministically fill missing operations."""
    allowed = set(batch.operations)
    by_id: dict[str, OperationFinding] = {}
    coverage_error = False
    for finding in result.findings:
        if finding.operation_id not in allowed or finding.operation_id in by_id:
            coverage_error = True
            continue
        by_id[finding.operation_id] = finding
    missing = [item for item in batch.operations if item not in by_id]
    if missing:
        coverage_error = True
    if not by_id:
        return deterministic_batch(batch), "deterministic_fallback", missing
    fallback = {item.operation_id: item for item in deterministic_batch(batch).findings}
    reconciled = BatchResult(
        findings=[by_id.get(item, fallback[item]) for item in batch.operations]
    )
    return reconciled, "partial_fallback" if coverage_error else "llm", missing


def _restrict_findings(result: BatchResult, batch: ExecutionBatch) -> BatchResult:
    """Prevent a model from introducing operations outside the active batch."""
    allowed = set(batch.operations)
    by_id = {
        finding.operation_id: finding
        for finding in result.findings
        if finding.operation_id in allowed
    }
    fallback = {item.operation_id: item for item in deterministic_batch(batch).findings}
    return BatchResult(
        findings=[by_id.get(item, fallback[item]) for item in batch.operations]
    )
