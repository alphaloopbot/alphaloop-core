"""Integration tests for API endpoints."""

from fastapi.testclient import TestClient
import pytest

from alphaloop_core.api import app

client = TestClient(app)


class TestAPIIntegration:
    """Integration tests for API endpoints."""

    @pytest.mark.skip(reason="API not implemented yet - integration tests require live services")
    def test_health_check_integration(self) -> None:
        """Test health check endpoint in integration environment."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "alphaloop-core"

    @pytest.mark.skip(reason="API not implemented yet - integration tests require live services")
    def test_admin_health_check_integration(self) -> None:
        """Test admin health check endpoint in integration environment."""
        response = client.get("/admin/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "alphaloop-core"
        assert data["version"] == "0.1.0"

    @pytest.mark.skip(reason="API not implemented yet - integration tests require live services")
    def test_root_endpoint_integration(self) -> None:
        """Test root endpoint in integration environment."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to AlphaLoop Core API"

    @pytest.mark.skip(reason="API not implemented yet - integration tests require live services")
    def test_api_status_integration(self) -> None:
        """Test API status endpoint in integration environment."""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["version"] == "0.1.0"
