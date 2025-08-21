"""Unit tests for API module."""

from fastapi.testclient import TestClient

from src.alphaloop_core.api import app

client = TestClient(app)


class TestAPI:
    """Test API endpoints."""

    def test_health_check(self) -> None:
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "alphaloop-core"

    def test_admin_health_check(self) -> None:
        """Test admin health check endpoint."""
        response = client.get("/admin/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "alphaloop-core"
        assert data["version"] == "0.1.0"
        assert "environment" in data
        assert "service_url" in data

    def test_root_endpoint(self) -> None:
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to AlphaLoop Core API"

    def test_api_status(self) -> None:
        """Test API status endpoint."""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["version"] == "0.1.0"
