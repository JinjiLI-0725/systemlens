"""FastAPI application entry point for SystemLens."""

from fastapi import FastAPI

from backend.api.routes import router


def create_app() -> FastAPI:
    """Create and configure the SystemLens API."""
    application = FastAPI(
        title="SystemLens API",
        description="Structured analysis through explicit thinking lenses.",
        version="0.1.0",
    )
    application.include_router(router)
    return application


app = create_app()
