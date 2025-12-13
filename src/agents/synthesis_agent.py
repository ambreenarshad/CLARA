"""Synthesis Agent - Generates comprehensive insights and reports."""

from typing import Dict, List, Optional

from src.services.nlp_processors import get_text_summarizer
from src.utils.config import get_config
from src.utils.logging_config import LogExecutionTime, get_logger

logger = get_logger(__name__)


class SynthesisAgent:
    """Agent responsible for synthesizing analysis results into reports."""

    def __init__(self):
        """Initialize Synthesis Agent."""
        self.config = get_config()
        self.text_summarizer = get_text_summarizer()
        logger.info("Synthesis Agent initialized")

    def generate_summary(
        self,
        texts: List[str],
        max_length: int = 500,
    ) -> str:
        """
        Generate overall summary from multiple texts.

        Args:
            texts: List of text documents
            max_length: Maximum summary length

        Returns:
            str: Generated summary
        """
        logger.info(f"Generating summary from {len(texts)} texts")

        if not texts:
            return "No feedback available for summarization."

        with LogExecutionTime(logger, "Summary generation"):
            # Combine texts for summarization
            combined_text = " ".join(texts[:50])  # Limit to first 50 for efficiency

            # Generate summary
            summary = self.text_summarizer.summarize(
                text=combined_text,
                max_sentences=5,
            )

            # Trim to max length
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."

            logger.info(f"Generated summary of length {len(summary)}")

            return summary

    def synthesize_emotion_insights(self, emotion_results: Dict) -> List[str]:
        """
        Generate insights from emotion analysis results.

        Args:
            emotion_results: Emotion analysis results

        Returns:
            List[str]: List of emotion insights
        """
        insights = []

        if not emotion_results:
            return insights

        # Dominant emotion
        dominant = emotion_results.get("dominant_emotion", "neutral")
        dist = emotion_results.get("emotion_distribution", {})
        avg_scores = emotion_results.get("average_scores", {})
        diversity = emotion_results.get("emotion_diversity", 0)

        total = sum(dist.values())

        if total > 0:
            # Primary emotion insight
            dominant_count = dist.get(dominant, 0)
            dominant_pct = (dominant_count / total) * 100

            if dominant_pct > 50:
                insights.append(f"Dominant emotion: {dominant.capitalize()} ({dominant_pct:.1f}% of feedback)")
            else:
                # Show top emotions
                sorted_emotions = sorted(dist.items(), key=lambda x: x[1], reverse=True)
                top_3 = sorted_emotions[:3]
                emotion_summary = ", ".join(
                    f"{e.capitalize()} ({(c/total)*100:.1f}%)"
                    for e, c in top_3
                )
                insights.append(f"Mixed emotions detected: {emotion_summary}")

            # Specific emotion highlights
            joy_pct = (dist.get("joy", 0) / total) * 100
            sadness_pct = (dist.get("sadness", 0) / total) * 100
            anger_pct = (dist.get("anger", 0) / total) * 100
            fear_pct = (dist.get("fear", 0) / total) * 100

            if joy_pct > 40:
                insights.append(f"✓ High levels of joy and satisfaction ({joy_pct:.1f}%)")

            if sadness_pct > 25:
                insights.append(f"Notable sadness detected ({sadness_pct:.1f}%) - investigate causes")

            if anger_pct > 20:
                insights.append(f"⚠️ Significant anger present ({anger_pct:.1f}%) - requires immediate attention")

            if fear_pct > 20:
                insights.append(f"Fear/anxiety detected ({fear_pct:.1f}%) - address concerns")

        # Emotion diversity insight
        if diversity > 0.75:
            insights.append("High emotional diversity - wide range of customer experiences")
        elif diversity < 0.3:
            insights.append("Low emotional diversity - consistent customer experience")

        return insights

    def synthesize_topic_insights(self, topic_results: Dict) -> List[str]:
        """
        Generate insights from topic modeling results.

        Args:
            topic_results: Topic modeling results

        Returns:
            List[str]: List of topic insights
        """
        insights = []

        if not topic_results:
            return insights

        num_topics = topic_results.get("num_topics", 0)
        topics = topic_results.get("topics", [])

        if num_topics == 0:
            insights.append("No distinct topics identified in feedback")
            return insights

        insights.append(f"Identified {num_topics} distinct discussion themes")

        # Analyze top topics
        if topics:
            # Sort by document count
            sorted_topics = sorted(topics, key=lambda t: t["count"], reverse=True)

            # Top 3 topics
            for idx, topic in enumerate(sorted_topics[:3], 1):
                keywords = ", ".join(topic["keywords"][:3])
                count = topic["count"]
                insights.append(
                    f"Theme #{idx}: {keywords} ({count} mentions)"
                )

            # Topic distribution analysis
            total_docs = sum(t["count"] for t in topics)
            top_topic_count = sorted_topics[0]["count"]
            top_topic_pct = (top_topic_count / total_docs) * 100 if total_docs > 0 else 0

            if top_topic_pct > 40:
                insights.append(
                    f"Dominant theme accounts for {top_topic_pct:.1f}% of feedback"
                )

        # Outliers
        outliers = topic_results.get("outliers", 0)
        if outliers > 0:
            insights.append(
                f"{outliers} feedback entries don't fit main themes (unique concerns)"
            )

        return insights

    def generate_recommendations(
        self,
        emotion_results: Dict,
        topic_results: Dict,
    ) -> List[str]:
        """
        Generate actionable recommendations based on analysis.

        Args:
            emotion_results: Emotion analysis results
            topic_results: Topic modeling results

        Returns:
            List[str]: List of recommendations
        """
        recommendations = []

        # Emotion-based recommendations
        if emotion_results:
            dist = emotion_results.get("emotion_distribution", {})
            avg_scores = emotion_results.get("average_scores", {})
            total = sum(dist.values())

            if total > 0:
                anger_pct = (dist.get("anger", 0) / total) * 100
                sadness_pct = (dist.get("sadness", 0) / total) * 100
                fear_pct = (dist.get("fear", 0) / total) * 100
                joy_pct = (dist.get("joy", 0) / total) * 100

                if anger_pct > 25:
                    recommendations.append(
                        "Priority: Address anger-inducing issues to improve satisfaction"
                    )

                if sadness_pct > 20:
                    recommendations.append(
                        "Investigate causes of sadness in customer feedback"
                    )

                if fear_pct > 15:
                    recommendations.append(
                        "Address customer concerns and anxieties to build trust"
                    )

                if joy_pct > 60:
                    recommendations.append(
                        "Leverage positive experiences in marketing and testimonials"
                    )

        # Topic-based recommendations
        if topic_results:
            topics = topic_results.get("topics", [])
            if topics:
                sorted_topics = sorted(topics, key=lambda t: t["count"], reverse=True)

                # Recommend focusing on top themes
                if len(sorted_topics) >= 1:
                    top_keywords = ", ".join(sorted_topics[0]["keywords"][:3])
                    recommendations.append(
                        f"Focus on most discussed theme: {top_keywords}"
                    )

        # General recommendations
        if not recommendations:
            recommendations.append(
                "Monitor feedback trends over time for emerging patterns"
            )

        return recommendations

    def synthesize_report(
        self,
        feedback_id: str,
        texts: List[str],
        emotion_results: Dict,
        topic_results: Dict,
        additional_insights: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate comprehensive analysis report.

        Args:
            feedback_id: Feedback batch ID
            texts: Original feedback texts
            emotion_results: Emotion analysis results
            topic_results: Topic modeling results
            additional_insights: Optional additional insights

        Returns:
            Dict: Comprehensive report
        """
        logger.info("Synthesizing comprehensive report")

        with LogExecutionTime(logger, "Report synthesis"):
            # Generate summary
            summary = self.generate_summary(texts)

            # Generate insights
            emotion_insights = self.synthesize_emotion_insights(emotion_results)
            topic_insights = self.synthesize_topic_insights(topic_results)

            # Combine all insights
            all_insights = emotion_insights + topic_insights
            if additional_insights:
                all_insights.extend(additional_insights)

            # Generate recommendations
            recommendations = self.generate_recommendations(
                emotion_results, topic_results
            )

            report = {
                "feedback_id": feedback_id,
                "summary": summary,
                "key_insights": all_insights,
                "recommendations": recommendations,
                "statistics": {
                    "total_feedback": len(texts),
                    "topics_identified": topic_results.get("num_topics", 0),
                    "dominant_emotion": emotion_results.get("dominant_emotion", "neutral"),
                    "emotion_diversity": emotion_results.get("emotion_diversity", 0),
                },
            }

            logger.info("Report synthesis complete")

            return report

    def create_executive_summary(self, report: Dict) -> str:
        """
        Create executive summary from full report.

        Args:
            report: Full analysis report

        Returns:
            str: Executive summary
        """
        stats = report.get("statistics", {})
        insights = report.get("key_insights", [])[:3]  # Top 3 insights

        exec_summary = f"""
EXECUTIVE SUMMARY
=================

Feedback Analysis: {stats.get('total_feedback', 0)} responses analyzed

Key Findings:
{chr(10).join(f'• {insight}' for insight in insights)}

Dominant Emotion: {stats.get('dominant_emotion', 'neutral').capitalize()}

Emotional Diversity: {stats.get('emotion_diversity', 0):.2f}

Topics Identified: {stats.get('topics_identified', 0)} major themes

For detailed analysis, see full report.
"""
        return exec_summary.strip()


# Global agent instance
_synthesis_agent: Optional[SynthesisAgent] = None


def get_synthesis_agent() -> SynthesisAgent:
    """
    Get global Synthesis Agent instance.

    Returns:
        SynthesisAgent: Global agent instance
    """
    global _synthesis_agent
    if _synthesis_agent is None:
        _synthesis_agent = SynthesisAgent()
    return _synthesis_agent
