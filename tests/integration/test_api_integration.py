"""Integration tests for API endpoints."""

from collections.abc import Generator

import httpx
import pytest

from src.alphaloop_core.config import settings


@pytest.fixture
def api_client() -> Generator[httpx.AsyncClient, None, None]:
    """Create an async HTTP client for API testing."""
    config = settings()
    base_url = config["SERVICE_URL"]

    with httpx.AsyncClient(base_url=base_url) as client:
        yield client


class TestAPIIntegration:
    """Integration tests for API endpoints."""

    @pytest.mark.asyncio
    async def test_health_check_integration(self, api_client: httpx.AsyncClient) -> None:
        """Test health check endpoint in integration environment."""
        response = await api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "alphaloop-core"

    @pytest.mark.asyncio
    async def test_admin_health_check_integration(self, api_client: httpx.AsyncClient) -> None:
        """Test admin health check endpoint in integration environment."""
        response = await api_client.get("/admin/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "alphaloop-core"
        assert data["version"] == "0.1.0"

    @pytest.mark.asyncio
    async def test_root_endpoint_integration(self, api_client: httpx.AsyncClient) -> None:
        """Test root endpoint in integration environment."""
        response = await api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to AlphaLoop Core API"

    @pytest.mark.asyncio
    async def test_api_status_integration(self, api_client: httpx.AsyncClient) -> None:
        """Test API status endpoint in integration environment."""
        response = await api_client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["version"] == "0.1.0"
