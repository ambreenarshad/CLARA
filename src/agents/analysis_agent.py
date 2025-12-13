"""Analysis Agent - Performs emotion analysis and topic modeling."""

from typing import Dict, List, Optional

from src.services.nlp_processors import (
    get_emotion_analyzer,
    get_topic_modeler,
)
from src.utils.config import get_config
from src.utils.logging_config import LogExecutionTime, get_logger

logger = get_logger(__name__)


class AnalysisAgent:
    """Agent responsible for emotion analysis and topic modeling."""

    def __init__(self):
        """Initialize Analysis Agent."""
        self.config = get_config()
        self.emotion_analyzer = get_emotion_analyzer()
        self.topic_modeler = get_topic_modeler()
        logger.info("Analysis Agent initialized")

    def analyze_emotions(self, texts: List[str]) -> Dict:
        """
        Perform emotion analysis on texts.

        Args:
            texts: List of text documents

        Returns:
            Dict: Emotion analysis results with scores and aggregations
        """
        logger.info(f"Analyzing emotions for {len(texts)} texts")

        with LogExecutionTime(logger, "Emotion analysis"):
            # Analyze each text
            emotions = self.emotion_analyzer.analyze_emotions(texts)

            # Aggregate results
            aggregated = self.emotion_analyzer.aggregate_emotions(emotions)

            # Extract dominant emotion labels for each text
            emotion_labels = [e.get("dominant_emotion", "neutral") for e in emotions]

            result = {
                "individual_emotions": emotions,
                "emotion_labels": emotion_labels,
                "aggregated": aggregated,
                "total_analyzed": len(texts),
            }

            logger.info(
                f"Emotion analysis complete: "
                f"{aggregated.get('emotion_distribution', {})}"
            )

            return result

    def extract_topics(
        self,
        texts: List[str],
        min_texts: int = 10,
    ) -> Dict:
        """
        Extract topics from texts using BERTopic.

        Args:
            texts: List of text documents
            min_texts: Minimum number of texts required

        Returns:
            Dict: Topic modeling results
        """
        logger.info(f"Extracting topics from {len(texts)} texts")

        with LogExecutionTime(logger, "Topic extraction"):
            # Extract topics
            topics_result = self.topic_modeler.extract_topics(texts, min_texts)

            # Get representative documents for each topic
            if topics_result["topics"]:
                for topic in topics_result["topics"]:
                    topic_id = topic["topic_id"]
                    repr_docs = self.topic_modeler.get_representative_docs(
                        topic_id, n_docs=3
                    )
                    topic["representative_docs"] = repr_docs

            logger.info(
                f"Topic extraction complete: "
                f"{topics_result.get('num_topics', 0)} topics found"
            )

            return topics_result

    def analyze(
        self,
        texts: List[str],
        include_topics: bool = True,
        include_emotions: bool = True,
    ) -> Dict:
        """
        Perform complete analysis (emotions + topics).

        Args:
            texts: List of text documents
            include_topics: Whether to include topic modeling
            include_emotions: Whether to include emotion analysis

        Returns:
            Dict: Complete analysis results
        """
        logger.info(f"Starting complete analysis of {len(texts)} texts")

        results = {
            "total_documents": len(texts),
            "analysis_performed": [],
        }

        # Emotion analysis
        if include_emotions:
            emotion_results = self.analyze_emotions(texts)
            results["emotions"] = emotion_results["aggregated"]
            results["individual_emotions"] = emotion_results["individual_emotions"]
            results["emotion_labels"] = emotion_results["emotion_labels"]
            results["analysis_performed"].append("emotions")

        # Topic modeling
        if include_topics and len(texts) >= 10:
            topic_results = self.extract_topics(texts)
            results["topics"] = topic_results
            results["analysis_performed"].append("topics")
        elif include_topics:
            logger.warning(
                f"Skipping topic modeling: insufficient texts ({len(texts)} < 10)"
            )
            results["topics"] = {
                "topics": [],
                "num_topics": 0,
                "message": "Insufficient texts for topic modeling",
            }

        logger.info(
            f"Complete analysis finished: {', '.join(results['analysis_performed'])}"
        )

        return results

    def get_insights(self, analysis_results: Dict) -> List[str]:
        """
        Generate key insights from analysis results.

        Args:
            analysis_results: Results from analyze()

        Returns:
            List[str]: List of key insights
        """
        insights = []

        # Emotion insights
        if "emotions" in analysis_results:
            emotions = analysis_results["emotions"]
            dist = emotions.get("emotion_distribution", {})
            avg_scores = emotions.get("average_scores", {})

            total = sum(dist.values())
            if total > 0:
                # Find dominant emotions
                sorted_emotions = sorted(dist.items(), key=lambda x: x[1], reverse=True)

                # Primary emotion insight
                primary_emotion, primary_count = sorted_emotions[0]
                primary_pct = (primary_count / total) * 100

                if primary_pct > 50:
                    insights.append(
                        f"Dominant emotion: {primary_emotion} ({primary_pct:.1f}% of feedback)"
                    )
                else:
                    # Show top 2-3 emotions if no clear dominant
                    top_emotions = sorted_emotions[:3]
                    emotion_summary = ", ".join(
                        f"{emotion} ({(count/total)*100:.1f}%)"
                        for emotion, count in top_emotions
                    )
                    insights.append(f"Mixed emotions: {emotion_summary}")

                # Specific emotion insights
                joy_pct = (dist.get("joy", 0) / total) * 100
                sadness_pct = (dist.get("sadness", 0) / total) * 100
                anger_pct = (dist.get("anger", 0) / total) * 100

                if joy_pct > 40:
                    insights.append(f"High levels of joy and satisfaction detected ({joy_pct:.1f}%)")
                if sadness_pct > 30:
                    insights.append(f"Notable sadness in feedback ({sadness_pct:.1f}%)")
                if anger_pct > 30:
                    insights.append(f"Significant anger detected - attention needed ({anger_pct:.1f}%)")

            # Emotion diversity
            diversity = emotions.get("emotion_diversity", 0)
            if diversity > 0.8:
                insights.append("High emotional diversity - feedback covers wide range of emotions")
            elif diversity < 0.3:
                insights.append("Low emotional diversity - feedback is emotionally uniform")

        # Topic insights
        if "topics" in analysis_results:
            topics = analysis_results["topics"]
            num_topics = topics.get("num_topics", 0)

            if num_topics > 0:
                insights.append(f"Identified {num_topics} distinct themes in feedback")

                # Highlight top topic
                topic_list = topics.get("topics", [])
                if topic_list:
                    top_topic = max(topic_list, key=lambda t: t["count"])
                    keywords = ", ".join(top_topic["keywords"][:3])
                    insights.append(
                        f"Most discussed theme: {keywords} ({top_topic['count']} mentions)"
                    )

        return insights


# Global agent instance
_analysis_agent: Optional[AnalysisAgent] = None


def get_analysis_agent() -> AnalysisAgent:
    """
    Get global Analysis Agent instance.

    Returns:
        AnalysisAgent: Global agent instance
    """
    global _analysis_agent
    if _analysis_agent is None:
        _analysis_agent = AnalysisAgent()
    return _analysis_agent
