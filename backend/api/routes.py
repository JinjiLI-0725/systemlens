"""HTTP routes for the SystemLens API."""

from fastapi import APIRouter

from backend.schemas.analysis import AnalysisRequest, AnalysisResponse
from backend.services.analysis import build_analysis

router = APIRouter()


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Report whether the API process is available."""
    return {"status": "ok"}


@router.post("/analyze", response_model=AnalysisResponse, tags=["analysis"])
def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """Run the deterministic SystemLens reasoning pipeline."""
    return build_analysis(request)
