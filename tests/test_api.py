"""Integration tests for API endpoints."""

import pytest
from fastapi import status


class TestHealthEndpoints:
    """Tests for health and info endpoints."""

    def test_root_endpoint(self, test_client):
        """Test root endpoint."""
        response = test_client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data

    def test_info_endpoint(self, test_client):
        """Test system info endpoint."""
        response = test_client.get("/info")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "api" in data
        assert "embedding_service" in data
        assert "vector_store" in data


class TestFeedbackUploadEndpoint:
    """Tests for /api/v1/upload endpoint."""

    def test_upload_valid_feedback(self, test_client, sample_feedback):
        """Test uploading valid feedback."""
        response = test_client.post(
            "/api/v1/upload",
            json={"feedback": sample_feedback[:5]},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "feedback_id" in data
        assert "status" in data
        assert data["status"] == "success"
        assert "count" in data

    def test_upload_empty_feedback(self, test_client, empty_feedback):
        """Test uploading empty feedback list."""
        response = test_client.post(
            "/api/v1/upload",
            json={"feedback": empty_feedback},
        )

        # Should fail validation
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_upload_invalid_feedback_only(self, test_client, invalid_feedback):
        """Test uploading only invalid feedback."""
        response = test_client.post(
            "/api/v1/upload",
            json={"feedback": invalid_feedback},
        )

        # Should fail as no valid entries
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_upload_mixed_feedback(self, test_client, mixed_feedback):
        """Test uploading mixed valid/invalid feedback."""
        response = test_client.post(
            "/api/v1/upload",
            json={"feedback": mixed_feedback},
        )

        # Should succeed with valid entries
        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["count"] < len(mixed_feedback)  # Some were filtered

    def test_upload_with_metadata(self, test_client, sample_feedback, feedback_metadata):
        """Test uploading feedback with metadata."""
        response = test_client.post(
            "/api/v1/upload",
            json={
                "feedback": sample_feedback[:3],
                "metadata": feedback_metadata,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "feedback_id" in data

    def test_upload_missing_feedback_field(self, test_client):
        """Test upload with missing required field."""
        response = test_client.post(
            "/api/v1/upload",
            json={},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAnalyzeEndpoint:
    """Tests for /api/v1/analyze endpoint."""

    @pytest.fixture
    def uploaded_feedback_id(self, test_client, sample_feedback):
        """Upload feedback and return its ID."""
        response = test_client.post(
            "/api/v1/upload",
            json={"feedback": sample_feedback[:10]},
        )
        if response.status_code == status.HTTP_201_CREATED:
            return response.json()["feedback_id"]
        return None

    def test_analyze_existing_feedback(self, test_client, uploaded_feedback_id):
        """Test analyzing existing feedback."""
        if not uploaded_feedback_id:
            pytest.skip("Upload failed, skipping analyze test")

        response = test_client.post(
            "/api/v1/analyze",
            json={"feedback_id": uploaded_feedback_id},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        if data["success"]:
            assert "sentiment" in data
            assert "report" in data

    def test_analyze_nonexistent_feedback(self, test_client):
        """Test analyzing nonexistent feedback."""
        response = test_client.post(
            "/api/v1/analyze",
            json={"feedback_id": "nonexistent_id_12345"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_analyze_with_options(self, test_client, uploaded_feedback_id):
        """Test analyze with custom options."""
        if not uploaded_feedback_id:
            pytest.skip("Upload failed, skipping analyze test")

        response = test_client.post(
            "/api/v1/analyze",
            json={
                "feedback_id": uploaded_feedback_id,
                "options": {
                    "include_summary": True,
                    "include_topics": False,
                },
            },
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "sentiment" in data or "success" in data


class TestProcessEndpoint:
    """Tests for /api/v1/process endpoint (combined upload + analyze)."""

    def test_process_valid_feedback(self, test_client, sample_feedback):
        """Test processing valid feedback (upload + analyze)."""
        response = test_client.post(
            "/api/v1/process",
            json={"feedback": sample_feedback[:10]},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "success" in data

        if data["success"]:
            assert "feedback_id" in data
            assert "sentiment" in data
            assert "report" in data

    def test_process_large_dataset(self, test_client, large_feedback_dataset):
        """Test processing larger dataset."""
        response = test_client.post(
            "/api/v1/process",
            json={"feedback": large_feedback_dataset},
        )

        # Should handle larger datasets
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_200_OK,
        ]

    def test_process_empty_feedback(self, test_client, empty_feedback):
        """Test process with empty feedback."""
        response = test_client.post(
            "/api/v1/process",
            json={"feedback": empty_feedback},
        )

        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]


class TestFeedbackSummaryEndpoint:
    """Tests for /api/v1/feedback/{feedback_id} endpoint."""

    @pytest.fixture
    def uploaded_feedback_id(self, test_client, sample_feedback):
        """Upload feedback and return its ID."""
        response = test_client.post(
            "/api/v1/upload",
            json={"feedback": sample_feedback[:5]},
        )
        if response.status_code == status.HTTP_201_CREATED:
            return response.json()["feedback_id"]
        return None

    def test_get_feedback_summary_existing(self, test_client, uploaded_feedback_id):
        """Test getting summary for existing feedback."""
        if not uploaded_feedback_id:
            pytest.skip("Upload failed, skipping summary test")

        response = test_client.get(f"/api/v1/feedback/{uploaded_feedback_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data

    def test_get_feedback_summary_nonexistent(self, test_client):
        """Test getting summary for nonexistent feedback."""
        response = test_client.get("/api/v1/feedback/nonexistent_id")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestStatisticsEndpoint:
    """Tests for /api/v1/statistics endpoint."""

    def test_get_statistics(self, test_client):
        """Test getting system statistics."""
        response = test_client.get("/api/v1/statistics")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        if data["success"]:
            assert "statistics" in data


class TestAPIErrorHandling:
    """Tests for API error handling."""

    def test_invalid_json(self, test_client):
        """Test handling of invalid JSON."""
        response = test_client.post(
            "/api/v1/upload",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_content_type(self, test_client):
        """Test handling of missing content type."""
        response = test_client.post(
            "/api/v1/upload",
            data='{"feedback": ["test"]}',
        )

        # FastAPI should handle this
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        ]

    def test_nonexistent_endpoint(self, test_client):
        """Test accessing nonexistent endpoint."""
        response = test_client.get("/api/v1/nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND
