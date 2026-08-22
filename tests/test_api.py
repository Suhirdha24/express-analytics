import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "vector_store" in data


def test_documents_endpoint():
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total_count" in data


def test_query_validation_empty():
    response = client.post("/query", json={"question": "   "})
    assert response.status_code == 400


def test_query_endpoint_success():
    response = client.post("/query", json={"question": "What is dependency injection?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "confidence_score" in data
    assert "workflow_trace" in data


def test_feedback_endpoint():
    payload = {
        "question": "What is dependency injection?",
        "answer": "Dependency injection is a design pattern...",
        "rating": "up",
        "comment": "Very clear explanation"
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "feedback_id" in data


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert "positive_feedback" in data
