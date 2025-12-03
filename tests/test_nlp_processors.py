"""Unit tests for NLP processors."""

import pytest

from src.services.nlp_processors import (
    SentimentAnalyzer,
    TextSummarizer,
    TopicModeler,
)


class TestSentimentAnalyzer:
    """Tests for SentimentAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create SentimentAnalyzer instance."""
        return SentimentAnalyzer()

    def test_analyze_positive_sentiment(self, analyzer):
        """Test positive sentiment detection."""
        text = "This is absolutely amazing! I love it so much!"
        result = analyzer.analyze_sentiment(text)

        assert "compound" in result
        assert "pos" in result
        assert result["compound"] > 0
        assert result["pos"] > result["neg"]

    def test_analyze_negative_sentiment(self, analyzer):
        """Test negative sentiment detection."""
        text = "This is terrible! I hate it. Worst experience ever."
        result = analyzer.analyze_sentiment(text)

        assert result["compound"] < 0
        assert result["neg"] > result["pos"]

    def test_analyze_neutral_sentiment(self, analyzer):
        """Test neutral sentiment detection."""
        text = "The product arrived on schedule."
        result = analyzer.analyze_sentiment(text)

        assert "compound" in result
        # Neutral should be close to 0
        assert -0.2 < result["compound"] < 0.2

    def test_analyze_empty_text(self, analyzer):
        """Test empty text handling."""
        result = analyzer.analyze_sentiment("")

        assert result["compound"] == 0.0
        assert result["neu"] == 1.0

    def test_analyze_batch_sentiments(self, analyzer, sample_feedback):
        """Test batch sentiment analysis."""
        results = analyzer.analyze_sentiments(sample_feedback)

        assert len(results) == len(sample_feedback)
        assert all("compound" in r for r in results)

    def test_get_sentiment_label(self, analyzer):
        """Test sentiment label conversion."""
        assert analyzer.get_sentiment_label(0.5) == "positive"
        assert analyzer.get_sentiment_label(-0.5) == "negative"
        assert analyzer.get_sentiment_label(0.0) == "neutral"

    def test_aggregate_sentiments(self, analyzer, sample_feedback):
        """Test sentiment aggregation."""
        sentiments = analyzer.analyze_sentiments(sample_feedback)
        aggregated = analyzer.aggregate_sentiments(sentiments)

        assert "average_compound" in aggregated
        assert "sentiment_distribution" in aggregated
        assert "positive" in aggregated["sentiment_distribution"]
        assert "negative" in aggregated["sentiment_distribution"]
        assert "neutral" in aggregated["sentiment_distribution"]


class TestTopicModeler:
    """Tests for TopicModeler."""

    @pytest.fixture
    def modeler(self):
        """Create TopicModeler instance."""
        return TopicModeler()

    def test_extract_topics_sufficient_data(self, modeler, large_feedback_dataset):
        """Test topic extraction with sufficient data."""
        result = modeler.extract_topics(large_feedback_dataset, min_texts=10)

        assert "topics" in result
        assert "topic_assignments" in result
        assert "num_topics" in result
        assert len(result["topic_assignments"]) == len(large_feedback_dataset)

    def test_extract_topics_insufficient_data(self, modeler, sample_feedback):
        """Test topic extraction with insufficient data."""
        result = modeler.extract_topics(sample_feedback[:5], min_texts=10)

        assert result["topics"] == []
        assert result["num_topics"] == 0 or "num_topics" not in result

    def test_topic_structure(self, modeler, large_feedback_dataset):
        """Test topic data structure."""
        result = modeler.extract_topics(large_feedback_dataset, min_texts=10)

        if result["topics"]:
            topic = result["topics"][0]
            assert "topic_id" in topic
            assert "keywords" in topic
            assert "scores" in topic
            assert "count" in topic
            assert isinstance(topic["keywords"], list)
            assert isinstance(topic["scores"], list)

    def test_get_representative_docs_not_fitted(self, modeler):
        """Test getting representative docs when model not fitted."""
        docs = modeler.get_representative_docs(topic_id=0)
        assert docs == []


class TestTextSummarizer:
    """Tests for TextSummarizer."""

    @pytest.fixture
    def summarizer(self):
        """Create TextSummarizer instance."""
        return TextSummarizer()

    def test_summarize_single_text(self, summarizer):
        """Test single text summarization."""
        text = (
            "The product quality is excellent. "
            "The customer service is outstanding. "
            "The delivery was very fast. "
            "The packaging was secure. "
            "Overall, I am very satisfied with my purchase. "
            "I would definitely recommend this to others. "
            "The price is reasonable for the quality. "
            "I will purchase again in the future."
        )

        summary = summarizer.summarize(text, max_sentences=3)

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert len(summary) < len(text)

    def test_summarize_empty_text(self, summarizer):
        """Test empty text summarization."""
        summary = summarizer.summarize("")
        assert summary == ""

    def test_summarize_short_text(self, summarizer):
        """Test short text summarization."""
        text = "This is a short sentence."
        summary = summarizer.summarize(text)

        assert isinstance(summary, str)
        # Short text might be returned as-is or slightly processed

    def test_summarize_multiple_texts(self, summarizer, sample_feedback):
        """Test batch summarization."""
        summaries = summarizer.summarize_multiple(sample_feedback[:5])

        assert len(summaries) == 5
        assert all(isinstance(s, str) for s in summaries)

    def test_extract_key_phrases(self, summarizer):
        """Test key phrase extraction."""
        text = (
            "The product quality is excellent and the customer service "
            "is outstanding. The delivery was fast and secure."
        )

        phrases = summarizer.extract_key_phrases(text, limit=5)

        assert isinstance(phrases, list)
        # Phrases should be tuples of (phrase, score)
        if phrases:
            assert all(isinstance(p, tuple) and len(p) == 2 for p in phrases)


class TestNLPProcessorIntegration:
    """Integration tests for NLP processors."""

    def test_complete_nlp_pipeline(
        self,
        sample_feedback,
    ):
        """Test complete NLP processing pipeline."""
        # Initialize all processors
        sentiment_analyzer = SentimentAnalyzer()
        text_summarizer = TextSummarizer()

        # Analyze sentiment
        sentiments = sentiment_analyzer.analyze_sentiments(sample_feedback)
        assert len(sentiments) == len(sample_feedback)

        # Aggregate sentiment
        aggregated = sentiment_analyzer.aggregate_sentiments(sentiments)
        assert "average_compound" in aggregated

        # Summarize feedback
        combined_text = " ".join(sample_feedback)
        summary = text_summarizer.summarize(combined_text, max_sentences=3)
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_processors_with_edge_cases(self):
        """Test processors with edge case inputs."""
        sentiment_analyzer = SentimentAnalyzer()
        text_summarizer = TextSummarizer()

        # Test with special characters
        special_text = "!!! @@@ ###"
        sentiment = sentiment_analyzer.analyze_sentiment(special_text)
        assert "compound" in sentiment

        # Test with very long text
        long_text = "Great product. " * 100
        summary = text_summarizer.summarize(long_text, max_sentences=2)
        assert len(summary) < len(long_text)

        # Test with mixed languages (should handle gracefully)
        mixed_text = "Good product. Très bien. Excelente."
        sentiment = sentiment_analyzer.analyze_sentiment(mixed_text)
        assert "compound" in sentiment
