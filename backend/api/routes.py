"""HTTP routes for the SystemLens API."""

from fastapi import APIRouter

from backend.schemas.analysis import AnalysisRequest, AnalysisResponse
from backend.services.analysis import build_mock_analysis

router = APIRouter()


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Report whether the API process is available."""
    return {"status": "ok"}


@router.post("/analyze", response_model=AnalysisResponse, tags=["analysis"])
def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """Return a deterministic, taxonomy-aligned mock analysis."""
    return build_mock_analysis(request)
