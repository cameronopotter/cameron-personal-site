"""
Tests for garden API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import json

from app.models.projects import Project
from app.models.skills import Skill
from app.models.visitors import Visitor


class TestGardenAPI:
    """Test garden API endpoints."""

    @pytest.mark.api
    def test_get_garden_data_success(self, client: TestClient, sample_project_data, sample_skill_data):
        """Test successful garden data retrieval."""
        response = client.get("/api/v1/garden/data")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "projects" in data
        assert "skills" in data
        assert "weather" in data
        assert "analytics" in data
        assert isinstance(data["projects"], list)
        assert isinstance(data["skills"], list)

    @pytest.mark.api
    async def test_get_garden_data_async(self, async_client: AsyncClient, async_session):
        """Test async garden data retrieval."""
        # Create test data
        project = Project(
            name="Test Project",
            description="Test Description",
            github_url="https://github.com/test/repo"
        )
        async_session.add(project)
        await async_session.commit()
        
        response = await async_client.get("/api/v1/garden/data")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 1
        assert data["projects"][0]["name"] == "Test Project"

    @pytest.mark.api
    @pytest.mark.performance
    async def test_garden_data_performance(self, async_client: AsyncClient, async_session, performance_monitor):
        """Test garden data endpoint performance."""
        # Create test data for performance testing
        for i in range(100):
            project = Project(
                name=f"Project {i}",
                description=f"Description {i}",
                github_url=f"https://github.com/test/repo{i}"
            )
            skill = Skill(
                name=f"Skill {i}",
                category="frontend",
                level=80
            )
            async_session.add_all([project, skill])
        
        await async_session.commit()
        
        # Monitor performance
        performance_monitor.start()
        
        response = await async_client.get("/api/v1/garden/data")
        
        performance_monitor.stop()
        
        assert response.status_code == 200
        assert performance_monitor.duration < 1.0  # Should complete within 1 second
        
        data = response.json()
        assert len(data["projects"]) == 100
        assert len(data["skills"]) == 100

    @pytest.mark.api
    def test_get_garden_layout(self, client: TestClient):
        """Test garden layout endpoint."""
        response = client.get("/api/v1/garden/layout")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "layout_type" in data
        assert "positions" in data
        assert "camera_settings" in data

    @pytest.mark.api
    @patch('app.services.garden.GardenService.calculate_optimal_layout')
    def test_optimize_garden_layout(self, mock_optimize, client: TestClient):
        """Test garden layout optimization."""
        mock_optimize.return_value = {
            "layout_type": "optimized",
            "positions": {"projects": [], "skills": []},
            "efficiency_score": 0.95
        }
        
        response = client.post("/api/v1/garden/optimize-layout", json={
            "algorithm": "genetic",
            "iterations": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["efficiency_score"] == 0.95
        assert data["layout_type"] == "optimized"
        mock_optimize.assert_called_once()

    @pytest.mark.api
    def test_get_garden_stats(self, client: TestClient):
        """Test garden statistics endpoint."""
        response = client.get("/api/v1/garden/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        expected_keys = [
            "total_projects", "total_skills", "active_projects",
            "skill_distribution", "growth_rate", "last_updated"
        ]
        for key in expected_keys:
            assert key in data

    @pytest.mark.api
    @pytest.mark.db
    async def test_update_project_position(self, async_client: AsyncClient, async_session):
        """Test updating project position in garden."""
        # Create a project
        project = Project(
            name="Test Project",
            description="Test Description",
            github_url="https://github.com/test/repo",
            position_x=0,
            position_y=0,
            position_z=0
        )
        async_session.add(project)
        await async_session.commit()
        await async_session.refresh(project)
        
        # Update position
        new_position = {"x": 10, "y": 5, "z": -2}
        response = await async_client.patch(
            f"/api/v1/garden/projects/{project.id}/position",
            json=new_position
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["position"]["x"] == 10
        assert data["position"]["y"] == 5
        assert data["position"]["z"] == -2

    @pytest.mark.api
    def test_get_garden_health(self, client: TestClient):
        """Test garden health check endpoint."""
        response = client.get("/api/v1/garden/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "components" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.api
    @pytest.mark.slow
    async def test_garden_growth_simulation(self, async_client: AsyncClient):
        """Test garden growth simulation."""
        response = await async_client.post("/api/v1/garden/simulate-growth", json={
            "days": 30,
            "growth_rate": 1.2,
            "include_weather": True
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "simulation_results" in data
        assert "projected_growth" in data
        assert "timeline" in data

    @pytest.mark.api
    def test_export_garden_data(self, client: TestClient):
        """Test garden data export."""
        response = client.get("/api/v1/garden/export", params={
            "format": "json",
            "include_positions": True
        })
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # Test CSV export
        response = client.get("/api/v1/garden/export", params={
            "format": "csv"
        })
        
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    @pytest.mark.api
    def test_garden_search(self, client: TestClient):
        """Test garden search functionality."""
        response = client.get("/api/v1/garden/search", params={
            "query": "react",
            "type": "both",  # projects and skills
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)

    @pytest.mark.api
    def test_invalid_garden_endpoints(self, client: TestClient):
        """Test error handling for invalid requests."""
        # Invalid project ID
        response = client.patch("/api/v1/garden/projects/999999/position", json={
            "x": 0, "y": 0, "z": 0
        })
        assert response.status_code == 404
        
        # Invalid search parameters
        response = client.get("/api/v1/garden/search", params={
            "limit": -1  # Invalid limit
        })
        assert response.status_code == 422
        
        # Invalid export format
        response = client.get("/api/v1/garden/export", params={
            "format": "invalid"
        })
        assert response.status_code == 400

    @pytest.mark.api
    @pytest.mark.security
    def test_garden_endpoint_security(self, client: TestClient):
        """Test security aspects of garden endpoints."""
        # Test SQL injection attempt
        response = client.get("/api/v1/garden/search", params={
            "query": "'; DROP TABLE projects; --"
        })
        assert response.status_code in [200, 400]  # Should not crash
        
        # Test XSS attempt in export
        response = client.get("/api/v1/garden/export", params={
            "format": "<script>alert('xss')</script>"
        })
        assert response.status_code == 400
        
        # Test oversized request
        large_positions = [{"x": i, "y": i, "z": i} for i in range(10000)]
        response = client.post("/api/v1/garden/bulk-update-positions", json={
            "positions": large_positions
        })
        # Should handle gracefully (either accept with limits or reject)
        assert response.status_code in [200, 413, 422]

    @pytest.mark.api
    @pytest.mark.performance
    async def test_concurrent_garden_requests(self, async_client: AsyncClient):
        """Test handling of concurrent garden requests."""
        import asyncio
        
        async def make_request():
            return await async_client.get("/api/v1/garden/data")
        
        # Make 50 concurrent requests
        tasks = [make_request() for _ in range(50)]
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "projects" in data
            assert "skills" in data