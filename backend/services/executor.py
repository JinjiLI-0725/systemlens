"""Provider-neutral batched operation execution."""

import json
from dataclasses import dataclass, field

from backend.llm.base import LLMProvider, LLMProviderError, Message
from backend.reasoning.operations import OPERATION_REGISTRY
from backend.schemas.execution import BatchResult, ExecutionBatch, OperationFinding


def batch_operations(
    operation_ids: list[str], maximum_size: int = 4
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
    metadata = [OPERATION_REGISTRY[item].as_dict() for item in batch.operations]
    system = (
        "You execute analytical operations and return JSON only. Treat every output as a "
        "preliminary hypothesis unless supported by evidence in the user input. Separate "
        "observations from inferences; surface assumptions and unknowns; preserve uncertainty. "
        "Never fabricate sources, citations, measurements, or evidence. Do not reveal hidden "
        "chain-of-thought; provide only concise conclusions and the requested structured fields."
    )
    user = (
        f"Problem:\n{problem}\n\nOperations metadata:\n"
        f"{json.dumps(metadata, indent=2)}\n\n"
        "Return an object with a 'findings' array containing exactly one item per operation. "
        "Each item must contain operation_id, observations, inferences, assumptions, unknowns, "
        "conclusions, and confidence (0 to 1). Use only operation IDs supplied above."
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


def execute_batches(
    problem: str, batches: list[ExecutionBatch], provider: LLMProvider
) -> BatchExecution:
    """Execute batches, repairing invalid output once before local fallback."""
    execution = BatchExecution()
    for batch in batches:
        messages = build_batch_messages(problem, batch)
        try:
            result = provider.generate_structured(messages, BatchResult)
            _validate_batch_result(result, batch)
        except LLMProviderError:
            repair = Message(
                role="user",
                content=(
                    "Repair the previous answer. Return valid JSON matching the requested fields "
                    "exactly; include one finding for every requested operation and no prose outside JSON."
                ),
            )
            try:
                result = provider.generate_structured([*messages, repair], BatchResult)
                _validate_batch_result(result, batch)
            except LLMProviderError:
                execution.fallbacks.append(
                    f"Batch '{batch.name}' failed validation after one repair; deterministic fallback used."
                )
                result = deterministic_batch(batch)
        execution.results.append(_restrict_findings(result, batch))
    return execution


def _validate_batch_result(result: BatchResult, batch: ExecutionBatch) -> None:
    """Require exactly one finding for every planned operation."""
    returned = [finding.operation_id for finding in result.findings]
    if len(returned) != len(set(returned)) or set(returned) != set(batch.operations):
        raise LLMProviderError(
            "Structured response did not cover the requested operations"
        )


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
