"""Internal schemas for validated operation-batch execution."""

from pydantic import BaseModel, Field


class OperationFinding(BaseModel):
    """Auditable output for one atomic operation, without hidden reasoning."""

    operation_id: str
    observations: list[str] = Field(default_factory=list)
    inferences: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    conclusions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class BatchResult(BaseModel):
    """Validated output for a logical group of operations."""

    findings: list[OperationFinding]


class ExecutionBatch(BaseModel):
    """A named, bounded group of planned operation identifiers."""

    name: str
    operations: list[str] = Field(min_length=1)


class BatchTiming(BaseModel):
    """Public-safe latency and fallback metadata for one execution batch."""

    batch_name: str
    elapsed_ms: int = Field(ge=0)
    fallback_used: bool
