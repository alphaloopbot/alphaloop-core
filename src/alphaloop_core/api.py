"""FastAPI application for AlphaLoop Core."""

from fastapi import FastAPI

from .config import settings

app = FastAPI(
    title="AlphaLoop Core API",
    description="A modern Python project with enterprise-grade tooling",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for service readiness."""
    return {"status": "ok", "service": "alphaloop-core"}


@app.get("/admin/health")
async def admin_health_check() -> dict[str, str]:
    """Detailed health check for admin purposes."""
    config = settings()
    return {
        "status": "ok",
        "service": "alphaloop-core",
        "version": "0.1.0",
        "environment": config["ENVIRONMENT"],
        "service_url": config["SERVICE_URL"],
    }


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to AlphaLoop Core API"}


@app.get("/api/v1/status")
async def api_status() -> dict[str, str]:
    """API status endpoint."""
    return {"status": "operational", "version": "0.1.0"}
