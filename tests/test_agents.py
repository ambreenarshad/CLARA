"""Unit tests for agents."""

import pytest

from src.agents.analysis_agent import AnalysisAgent
from src.agents.data_ingestion_agent import DataIngestionAgent
from src.agents.orchestrator import AgentOrchestrator
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.synthesis_agent import SynthesisAgent


class TestDataIngestionAgent:
    """Tests for DataIngestionAgent."""

    @pytest.fixture
    def agent(self):
        """Create DataIngestionAgent instance."""
        return DataIngestionAgent()

    def test_clean_text(self, agent):
        """Test text cleaning."""
        dirty_text = "  This   is   a    test!  "
        cleaned = agent.clean_text(dirty_text)

        assert cleaned == "This is a test!"
        assert "  " not in cleaned

    def test_clean_text_with_url(self, agent):
        """Test cleaning text with URLs."""
        text = "Check this out http://example.com great stuff!"
        cleaned = agent.clean_text(text)

        assert "http" not in cleaned
        assert "example.com" not in cleaned

    def test_clean_text_with_email(self, agent):
        """Test cleaning text with email."""
        text = "Contact me at test@example.com for more info."
        cleaned = agent.clean_text(text)

        assert "@" not in cleaned
        assert "test@example.com" not in cleaned

    def test_validate_feedback_all_valid(self, agent, sample_feedback):
        """Test validation with all valid feedback."""
        result = agent.validate_feedback(sample_feedback)

        assert result["valid_count"] > 0
        assert result["invalid_count"] == 0
        assert len(result["cleaned_texts"]) == result["valid_count"]

    def test_validate_feedback_all_invalid(self, agent, invalid_feedback):
        """Test validation with all invalid feedback."""
        result = agent.validate_feedback(invalid_feedback)

        assert result["valid_count"] == 0
        assert result["invalid_count"] > 0
        assert len(result["cleaned_texts"]) == 0

    def test_validate_feedback_mixed(self, agent, mixed_feedback):
        """Test validation with mixed valid/invalid feedback."""
        result = agent.validate_feedback(mixed_feedback)

        assert result["valid_count"] > 0
        assert result["invalid_count"] > 0
        assert result["valid_count"] + result["invalid_count"] == len(mixed_feedback)

    def test_validate_empty_feedback(self, agent, empty_feedback):
        """Test validation with empty feedback list."""
        result = agent.validate_feedback(empty_feedback)

        assert result["valid_count"] == 0
        assert result["invalid_count"] == 0


class TestAnalysisAgent:
    """Tests for AnalysisAgent."""

    @pytest.fixture
    def agent(self):
        """Create AnalysisAgent instance."""
        return AnalysisAgent()

    def test_analyze_sentiment(self, agent, sample_feedback):
        """Test sentiment analysis."""
        result = agent.analyze_sentiment(sample_feedback)

        assert "individual_sentiments" in result
        assert "sentiment_labels" in result
        assert "aggregated" in result
        assert len(result["individual_sentiments"]) == len(sample_feedback)

    def test_extract_topics_sufficient_data(self, agent, large_feedback_dataset):
        """Test topic extraction with sufficient data."""
        result = agent.extract_topics(large_feedback_dataset, min_texts=10)

        assert "topics" in result
        assert "num_topics" in result

    def test_extract_topics_insufficient_data(self, agent, sample_feedback):
        """Test topic extraction with insufficient data."""
        result = agent.extract_topics(sample_feedback[:5], min_texts=10)

        # Should handle gracefully
        assert "topics" in result

    def test_analyze_full(self, agent, sample_feedback):
        """Test complete analysis."""
        result = agent.analyze(
            sample_feedback,
            include_topics=False,  # Skip topics for faster test
            include_sentiment=True,
        )

        assert "total_documents" in result
        assert "sentiment" in result
        assert "analysis_performed" in result
        assert "sentiment" in result["analysis_performed"]

    def test_get_insights(self, agent, sample_feedback):
        """Test insight generation."""
        analysis_result = agent.analyze(
            sample_feedback,
            include_topics=False,
            include_sentiment=True,
        )

        insights = agent.get_insights(analysis_result)

        assert isinstance(insights, list)
        assert len(insights) > 0


class TestRetrievalAgent:
    """Tests for RetrievalAgent."""

    @pytest.fixture
    def agent(self):
        """Create RetrievalAgent instance."""
        return RetrievalAgent()

    def test_retrieve_similar_empty_query(self, agent):
        """Test retrieval with empty query."""
        result = agent.retrieve_similar("", n_results=5)

        # Should handle gracefully
        assert "success" in result

    def test_get_representative_samples_no_data(self, agent):
        """Test getting samples when no data exists."""
        result = agent.get_representative_samples(
            feedback_id="nonexistent",
            n_samples=5,
        )

        assert "success" in result
        if result["success"]:
            assert "samples" in result


class TestSynthesisAgent:
    """Tests for SynthesisAgent."""

    @pytest.fixture
    def agent(self):
        """Create SynthesisAgent instance."""
        return SynthesisAgent()

    def test_generate_summary(self, agent, sample_feedback):
        """Test summary generation."""
        summary = agent.generate_summary(sample_feedback, max_length=200)

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert len(summary) <= 210  # Allow some margin

    def test_generate_summary_empty_texts(self, agent, empty_feedback):
        """Test summary with empty texts."""
        summary = agent.generate_summary(empty_feedback)

        assert isinstance(summary, str)
        assert "no feedback" in summary.lower() or summary == ""

    def test_synthesize_sentiment_insights(self, agent):
        """Test sentiment insight synthesis."""
        sentiment_results = {
            "average_compound": 0.6,
            "sentiment_distribution": {
                "positive": 70,
                "neutral": 20,
                "negative": 10,
            },
        }

        insights = agent.synthesize_sentiment_insights(sentiment_results)

        assert isinstance(insights, list)
        assert len(insights) > 0

    def test_synthesize_topic_insights(self, agent):
        """Test topic insight synthesis."""
        topic_results = {
            "num_topics": 3,
            "topics": [
                {
                    "topic_id": 0,
                    "keywords": ["quality", "product", "excellent"],
                    "count": 25,
                },
                {
                    "topic_id": 1,
                    "keywords": ["service", "customer", "support"],
                    "count": 15,
                },
            ],
            "outliers": 5,
        }

        insights = agent.synthesize_topic_insights(topic_results)

        assert isinstance(insights, list)
        assert len(insights) > 0

    def test_generate_recommendations(self, agent):
        """Test recommendation generation."""
        sentiment_results = {
            "average_compound": -0.2,
            "sentiment_distribution": {
                "positive": 30,
                "neutral": 40,
                "negative": 30,
            },
        }

        topic_results = {
            "num_topics": 2,
            "topics": [
                {
                    "topic_id": 0,
                    "keywords": ["delivery", "shipping", "late"],
                    "count": 20,
                }
            ],
        }

        recommendations = agent.generate_recommendations(
            sentiment_results, topic_results
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_create_executive_summary(self, agent):
        """Test executive summary creation."""
        report = {
            "statistics": {
                "total_feedback": 100,
                "topics_identified": 5,
                "average_sentiment": 0.3,
            },
            "key_insights": [
                "70% positive feedback",
                "Main concerns about delivery",
                "High satisfaction with product quality",
            ],
        }

        exec_summary = agent.create_executive_summary(report)

        assert isinstance(exec_summary, str)
        assert "EXECUTIVE SUMMARY" in exec_summary
        assert "100" in exec_summary


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create AgentOrchestrator instance."""
        return AgentOrchestrator()

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes all agents."""
        assert orchestrator.ingestion_agent is not None
        assert orchestrator.analysis_agent is not None
        assert orchestrator.retrieval_agent is not None
        assert orchestrator.synthesis_agent is not None

    def test_process_feedback_empty_list(self, orchestrator, empty_feedback):
        """Test processing empty feedback list."""
        result = orchestrator.process_feedback(empty_feedback)

        # Should fail gracefully
        assert "success" in result
        if not result["success"]:
            assert "error" in result

    def test_process_feedback_invalid_only(self, orchestrator, invalid_feedback):
        """Test processing only invalid feedback."""
        result = orchestrator.process_feedback(invalid_feedback)

        # Should fail with no valid data
        assert "success" in result

    def test_get_feedback_summary_nonexistent(self, orchestrator):
        """Test getting summary for nonexistent feedback."""
        result = orchestrator.get_feedback_summary("nonexistent_id")

        assert "success" in result
        assert result["success"] is False
        assert "error" in result
