"""Integration tests for FastAPI endpoints with mocked Gemini calls."""

import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /api/health returns 200 OK and status 'ok'."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tailor_endpoint_validation_error():
    """Verify POST /api/tailor returns HTTP 422 for payloads with <15 chars or missing fields."""
    # Under 15 chars in resume
    resp_short_resume = client.post(
        "/api/tailor",
        json={
            "resume_text": "Short",
            "job_description": "Valid job description with sufficient characters here."
        }
    )
    assert resp_short_resume.status_code == 422

    # Under 15 chars in JD
    resp_short_jd = client.post(
        "/api/tailor",
        json={
            "resume_text": "Valid resume experience bullets with sufficient length here.",
            "job_description": "Short"
        }
    )
    assert resp_short_jd.status_code == 422

    # Missing field
    resp_missing = client.post(
        "/api/tailor",
        json={"resume_text": "Valid resume experience bullets with sufficient length."}
    )
    assert resp_missing.status_code == 422


def test_tailor_endpoint_exceeds_max_length():
    """Verify POST /api/tailor returns HTTP 422 when text exceeds 12,000 characters."""
    oversized = "X" * 12001
    resp = client.post(
        "/api/tailor",
        json={
            "resume_text": oversized,
            "job_description": "Valid job description with sufficient length here."
        }
    )
    assert resp.status_code == 422


@patch("gemini_service.create_gemini_client")
def test_tailor_endpoint_success(mock_create_client):
    """Verify POST /api/tailor returns 200 and structured bullets on successful model response."""
    # Mock Gemini response
    mock_genai_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "bullets": [
            {
                "original_bullet": "Worked on API performance and fixed database queries",
                "tailored_bullet": "Improved API performance by optimizing database queries.",
                "why": "Rephrased to emphasize proactive database optimization matching the job posting's API performance requirements."
            }
        ]
    })
    mock_genai_client.models.generate_content.return_value = mock_response
    mock_create_client.return_value = mock_genai_client

    payload = {
        "resume_text": "• Worked on API performance and fixed database queries\n• Built automated test suite for order processing",
        "job_description": "Seeking Backend Engineer experienced in API performance and database optimization."
    }

    response = client.post("/api/tailor", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "bullets" in data
    assert len(data["bullets"]) == 1
    assert data["bullets"][0]["original_bullet"] == "Worked on API performance and fixed database queries"
    assert data["bullets"][0]["tailored_bullet"] == "Improved API performance by optimizing database queries."
    assert "why" in data["bullets"][0]


@patch("gemini_service.create_gemini_client")
def test_tailor_endpoint_gemini_error_handling(mock_create_client):
    """Verify POST /api/tailor returns HTTP 502 with friendly error message on upstream timeout or failure."""
    mock_genai_client = MagicMock()
    # Simulate an upstream timeout or connection error (>15000ms)
    mock_genai_client.models.generate_content.side_effect = TimeoutError("Request timed out after 15000ms")
    mock_create_client.return_value = mock_genai_client

    payload = {
        "resume_text": "• Worked on API performance and fixed database queries\n• Built automated test suite for order processing",
        "job_description": "Seeking Backend Engineer experienced in API performance and database optimization."
    }

    response = client.post("/api/tailor", json=payload)
    assert response.status_code == 502
    data = response.json()
    assert "Unable to tailor bullets right now" in data["detail"]
