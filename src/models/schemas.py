"""Pydantic models for API request and response schemas."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# Request Models
class FeedbackUploadRequest(BaseModel):
    """Request model for uploading feedback data."""

    feedback: List[str] = Field(
        ...,
        description="List of feedback text entries",
        min_length=1,
    )
    metadata: Optional[List[Dict]] = Field(
        default=None,
        description="Optional metadata for each feedback entry",
    )

    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, v: List[str]) -> List[str]:
        """Validate feedback entries are non-empty."""
        if not v:
            raise ValueError("Feedback list cannot be empty")

        # Filter out empty strings
        valid_feedback = [f.strip() for f in v if f and f.strip()]

        if not valid_feedback:
            raise ValueError("All feedback entries are empty")

        return valid_feedback

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "feedback": [
                        "Great product, very satisfied!",
                        "Terrible service, never ordering again.",
                        "Average experience, could be better.",
                    ]
                }
            ]
        }
    }


class AnalysisRequest(BaseModel):
    """Request model for triggering feedback analysis."""

    feedback_id: str = Field(
        ...,
        description="ID of uploaded feedback to analyze",
    )
    options: Optional[Dict] = Field(
        default=None,
        description="Analysis options (e.g., include_summary, max_topics)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "feedback_id": "feedback_12345",
                    "options": {"include_summary": True, "max_topics": 5},
                }
            ]
        }
    }


# Response Models
class FeedbackUploadResponse(BaseModel):
    """Response model for feedback upload."""

    feedback_id: str = Field(..., description="Unique ID for the uploaded feedback")
    status: str = Field(..., description="Upload status")
    count: int = Field(..., description="Number of feedback entries uploaded")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "feedback_id": "feedback_12345",
                    "status": "success",
                    "count": 150,
                    "timestamp": "2025-12-03T10:30:00Z",
                }
            ]
        }
    }


class EmotionAnalysisResult(BaseModel):
    """Emotion analysis results."""

    average_scores: Dict[str, float] = Field(
        ...,
        description="Average scores for each emotion (joy, sadness, anger, fear, surprise, neutral)",
    )
    emotion_distribution: Dict[str, int] = Field(
        ...,
        description="Count of dominant emotion for each feedback",
    )
    dominant_emotion: str = Field(..., description="Overall dominant emotion")
    emotion_diversity: float = Field(
        ...,
        description="Emotion diversity score (0-1, higher = more diverse)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "average_scores": {
                        "joy": 0.35,
                        "sadness": 0.15,
                        "anger": 0.10,
                        "fear": 0.12,
                        "surprise": 0.08,
                        "neutral": 0.20,
                    },
                    "emotion_distribution": {
                        "joy": 45,
                        "sadness": 20,
                        "anger": 10,
                        "fear": 8,
                        "surprise": 7,
                        "neutral": 10,
                    },
                    "dominant_emotion": "joy",
                    "emotion_diversity": 0.75,
                }
            ]
        }
    }


class Topic(BaseModel):
    """Topic model representation."""

    topic_id: int = Field(..., description="Topic ID")
    keywords: List[str] = Field(..., description="Top keywords for the topic")
    scores: List[float] = Field(..., description="Keyword relevance scores")
    count: int = Field(..., description="Number of documents in topic")
    representative_docs: Optional[List[str]] = Field(
        default=None,
        description="Representative documents",
    )


class TopicModelingResult(BaseModel):
    """Topic modeling results."""

    topics: List[Topic] = Field(..., description="Extracted topics")
    num_topics: int = Field(..., description="Number of topics found")
    outliers: int = Field(..., description="Number of outlier documents")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "topics": [
                        {
                            "topic_id": 0,
                            "keywords": ["quality", "product", "excellent"],
                            "scores": [0.95, 0.87, 0.82],
                            "count": 45,
                        }
                    ],
                    "num_topics": 5,
                    "outliers": 8,
                }
            ]
        }
    }


class AnalysisResponse(BaseModel):
    """Complete analysis response."""

    feedback_id: str = Field(..., description="Feedback batch ID")
    status: str = Field(..., description="Analysis status")
    emotions: EmotionAnalysisResult = Field(..., description="Emotion analysis results")
    topics: TopicModelingResult = Field(..., description="Topic modeling results")
    summary: Optional[str] = Field(None, description="Overall summary")
    key_insights: List[str] = Field(
        default_factory=list,
        description="Key insights extracted",
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "feedback_id": "feedback_12345",
                    "status": "completed",
                    "emotions": {
                        "average_scores": {
                            "joy": 0.45,
                            "sadness": 0.10,
                            "anger": 0.05,
                            "fear": 0.08,
                            "surprise": 0.12,
                            "neutral": 0.20,
                        },
                        "emotion_distribution": {
                            "joy": 60,
                            "sadness": 15,
                            "anger": 5,
                            "fear": 8,
                            "surprise": 7,
                            "neutral": 5,
                        },
                        "dominant_emotion": "joy",
                        "emotion_diversity": 0.68,
                    },
                    "topics": {"num_topics": 5, "outliers": 8},
                    "summary": "Overall joyful feedback about product quality...",
                    "key_insights": [
                        "Dominant emotion: joy (60% of feedback)",
                        "Main concerns about delivery time",
                    ],
                    "timestamp": "2025-12-03T10:35:00Z",
                }
            ]
        }
    }


class RetrievalResult(BaseModel):
    """RAG retrieval result."""

    documents: List[str] = Field(..., description="Retrieved documents")
    distances: List[float] = Field(..., description="Distance scores")
    metadata: List[Dict] = Field(..., description="Document metadata")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "Invalid feedback ID",
                    "detail": "Feedback ID 'xyz' not found in database",
                    "timestamp": "2025-12-03T10:35:00Z",
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    embedding_service: Optional[str] = None
    embedding_model: Optional[str] = None
    vector_store: Optional[str] = None
    document_count: Optional[str] = None
    error: Optional[str] = None
