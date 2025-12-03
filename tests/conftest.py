"""Pytest configuration and fixtures."""

import json
import os
from pathlib import Path
from typing import Dict, List

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_feedback() -> List[str]:
    """Sample feedback texts for testing."""
    return [
        "The product quality is absolutely outstanding! I'm very impressed.",
        "Terrible customer service. Waited for hours with no response.",
        "Good value for money. Works as expected.",
        "Very disappointed with the packaging. Item arrived damaged.",
        "Excellent experience! Will definitely recommend.",
        "The product description was misleading.",
        "Amazing quality and fast shipping!",
        "Customer support was very helpful.",
        "The price is too high for what you get.",
        "Perfect! Exactly what I was looking for.",
        "Had some issues but support helped me.",
        "Not satisfied with the quality. Feels cheap.",
        "Great product but delivery took long.",
        "Absolutely love it! Best purchase this year.",
        "The interface is confusing and hard to navigate.",
    ]


@pytest.fixture
def sample_feedback_json() -> Dict:
    """Sample feedback in JSON format."""
    test_data_path = Path(__file__).parent.parent / "test_data" / "sample_feedback.json"

    if test_data_path.exists():
        with open(test_data_path, "r") as f:
            return json.load(f)

    # Fallback
    return {
        "feedback": [
            "Great product!",
            "Terrible service.",
            "Average experience.",
        ]
    }


@pytest.fixture
def large_feedback_dataset() -> List[str]:
    """Large feedback dataset for testing topic modeling."""
    base_feedback = [
        "Excellent product quality and fast delivery. Very satisfied!",
        "Poor customer service. Never ordering again.",
        "Good value for the price. Recommended.",
        "Packaging was terrible. Item damaged on arrival.",
        "Amazing experience from start to finish!",
        "Product doesn't match description. Disappointed.",
        "Fast shipping and great quality. Five stars!",
        "Support team was incredibly helpful and responsive.",
        "Way too expensive for what you actually get.",
        "Perfect product! Exceeded all expectations.",
    ]

    # Repeat to get enough data for topic modeling
    return base_feedback * 6  # 60 items


@pytest.fixture
def empty_feedback() -> List[str]:
    """Empty feedback list for testing edge cases."""
    return []


@pytest.fixture
def invalid_feedback() -> List[str]:
    """Invalid feedback for testing validation."""
    return [
        "",  # Empty string
        "   ",  # Whitespace only
        "ok",  # Too short (less than 3 words)
        "http://spam.com",  # URL only
        "!!!",  # Special characters only
    ]


@pytest.fixture
def mixed_feedback() -> List[str]:
    """Mix of valid and invalid feedback."""
    return [
        "This is a great product with excellent quality.",  # Valid
        "",  # Invalid - empty
        "Terrible service and poor communication.",  # Valid
        "ok",  # Invalid - too short
        "Average experience, nothing special here.",  # Valid
    ]


@pytest.fixture
def feedback_metadata() -> List[Dict]:
    """Sample metadata for feedback."""
    return [
        {"source": "website", "rating": 5, "user_id": "user_001"},
        {"source": "email", "rating": 1, "user_id": "user_002"},
        {"source": "survey", "rating": 3, "user_id": "user_003"},
    ]


@pytest.fixture
def test_client():
    """FastAPI test client."""
    from src.api.main import app

    return TestClient(app)


@pytest.fixture
def cleanup_chromadb():
    """Cleanup ChromaDB after tests."""
    yield

    # Cleanup logic
    try:
        from src.services.vectorstore import get_vector_store_service
        vector_store = get_vector_store_service()
        # Note: In production, you might want to use a separate test database
        # For now, we'll just get the service ready
    except Exception:
        pass


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "models": {
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "spacy_model": "en_core_web_sm",
        },
        "nlp": {
            "min_topic_size": 5,
            "max_topics": 5,
            "sentiment_threshold": 0.05,
        },
    }


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("LOG_LEVEL", "ERROR")  # Reduce logging noise in tests
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "./test_chroma_db")
