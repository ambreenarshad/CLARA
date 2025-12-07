"""
Result Display Components for Analysis Results
"""

import streamlit as st
from typing import Dict, Any, List
from src.ui.utils.formatters import (
    format_sentiment_score,
    format_sentiment_label,
    format_sentiment_emoji,
    format_sentiment_color,
    format_large_number,
    format_topic_label,
    truncate_text
)


def display_overview(analysis_results: Dict[str, Any]):
    """
    Display analysis overview with key metrics

    Args:
        analysis_results: Complete analysis results dictionary
    """
    st.subheader("📊 Overview")

    # Extract data
    feedback_id = analysis_results.get('feedback_id', 'N/A')
    sentiment = analysis_results.get('sentiment', {})
    topics = analysis_results.get('topics', {})

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        compound = sentiment.get('average_compound', 0)
        emoji = format_sentiment_emoji(compound)
        label = format_sentiment_label(compound)
        st.metric(
            "Overall Sentiment",
            f"{emoji} {label}",
            delta=f"{compound:+.2f}" if compound != 0 else None
        )

    with col2:
        num_topics = topics.get('num_topics', 0)
        st.metric("Topics Discovered", num_topics)

    with col3:
        distribution = sentiment.get('sentiment_distribution', {})
        positive_count = distribution.get('positive', 0)
        st.metric("Positive Feedback", positive_count)

    with col4:
        outliers = topics.get('outliers', 0)
        st.metric("Outliers", outliers, help="Feedback items that don't fit into any topic")

    # Feedback ID
    st.caption(f"**Feedback Batch ID:** `{feedback_id}`")


def display_sentiment_analysis(sentiment_data: Dict[str, Any]):
    """
    Display detailed sentiment analysis results

    Args:
        sentiment_data: Sentiment analysis dictionary
    """
    st.subheader("😊 Sentiment Analysis")

    # Sentiment scores
    st.markdown("### Aggregate Scores")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        compound = sentiment_data.get('average_compound', 0)
        color = format_sentiment_color(compound)
        st.markdown(f"**Compound Score**")
        st.markdown(f"<h2 style='color: {color};'>{compound:.3f}</h2>", unsafe_allow_html=True)
        st.caption("Range: -1 (negative) to +1 (positive)")

    with col2:
        positive = sentiment_data.get('average_positive', 0)
        st.metric("Positive Score", f"{positive:.3f}")

    with col3:
        neutral = sentiment_data.get('average_neutral', 0)
        st.metric("Neutral Score", f"{neutral:.3f}")

    with col4:
        negative = sentiment_data.get('average_negative', 0)
        st.metric("Negative Score", f"{negative:.3f}")

    # Distribution
    st.markdown("### Sentiment Distribution")

    distribution = sentiment_data.get('sentiment_distribution', {})

    col1, col2, col3 = st.columns(3)

    with col1:
        positive_count = distribution.get('positive', 0)
        st.success(f"😊 **Positive:** {positive_count}")

    with col2:
        neutral_count = distribution.get('neutral', 0)
        st.info(f"😐 **Neutral:** {neutral_count}")

    with col3:
        negative_count = distribution.get('negative', 0)
        st.error(f"😞 **Negative:** {negative_count}")

    # Percentage breakdown
    total = positive_count + neutral_count + negative_count

    if total > 0:
        pos_pct = (positive_count / total) * 100
        neu_pct = (neutral_count / total) * 100
        neg_pct = (negative_count / total) * 100

        st.caption(f"Positive: {pos_pct:.1f}% | Neutral: {neu_pct:.1f}% | Negative: {neg_pct:.1f}%")


def display_topic_modeling(topics_data: Dict[str, Any]):
    """
    Display topic modeling results

    Args:
        topics_data: Topic modeling dictionary
    """
    st.subheader("🏷️ Topic Modeling")

    num_topics = topics_data.get('num_topics', 0)
    topics_list = topics_data.get('topics', [])
    outliers = topics_data.get('outliers', 0)

    if num_topics == 0:
        st.warning("No topics were discovered in this dataset.")
        return

    st.markdown(f"**{num_topics} topics discovered** (excluding {outliers} outliers)")

    # Display each topic
    for topic in topics_list:
        topic_id = topic.get('topic_id', -1)

        # Skip outliers topic
        if topic_id == -1:
            continue

        keywords = topic.get('keywords', [])
        scores = topic.get('scores', [])
        count = topic.get('count', 0)

        # Topic card
        with st.expander(f"📌 {format_topic_label(topic_id, keywords)}", expanded=(topic_id < 3)):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("**Top Keywords:**")

                # Display keywords with scores
                keyword_data = []
                for i, (keyword, score) in enumerate(zip(keywords[:10], scores[:10])):
                    keyword_data.append({
                        'Rank': i + 1,
                        'Keyword': keyword,
                        'Relevance': f"{score:.3f}"
                    })

                st.dataframe(keyword_data, use_container_width=True, hide_index=True)

            with col2:
                st.metric("Documents", count)
                st.caption(f"Topic {topic_id}")

            # Representative documents (if available)
            rep_docs = topic.get('representative_docs', [])
            if rep_docs:
                st.markdown("**Representative Feedback:**")
                for i, doc in enumerate(rep_docs[:3]):
                    st.info(f"💬 {truncate_text(doc, 200)}")


def display_report(report_data: Dict[str, Any]):
    """
    Display generated report

    Args:
        report_data: Report dictionary
    """
    st.subheader("📝 Generated Report")

    # Key insights
    if 'key_insights' in report_data and report_data['key_insights']:
        st.markdown("### 🔑 Key Insights")
        for insight in report_data['key_insights']:
            st.markdown(f"- {insight}")

    # Recommendations
    if 'recommendations' in report_data and report_data['recommendations']:
        st.markdown("### 💡 Recommendations")
        for i, recommendation in enumerate(report_data['recommendations'], 1):
            st.markdown(f"{i}. {recommendation}")

    # Summary
    if 'summary' in report_data and report_data['summary']:
        st.markdown("### 📄 Executive Summary")
        st.markdown(report_data['summary'])

    # Full report (if available)
    if 'full_report' in report_data:
        with st.expander("View Full Report"):
            st.markdown(report_data['full_report'])


def display_complete_results(analysis_results: Dict[str, Any]):
    """
    Display complete analysis results with tabs

    Args:
        analysis_results: Complete analysis results dictionary
    """
    # Tabs for different result sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "😊 Sentiment", "🏷️ Topics", "📝 Report"])

    with tab1:
        display_overview(analysis_results)

    with tab2:
        sentiment = analysis_results.get('sentiment', {})
        if sentiment:
            display_sentiment_analysis(sentiment)
        else:
            st.warning("No sentiment analysis data available.")

    with tab3:
        topics = analysis_results.get('topics', {})
        if topics:
            display_topic_modeling(topics)
        else:
            st.warning("No topic modeling data available.")

    with tab4:
        report = analysis_results.get('report', {})
        if report:
            display_report(report)
        else:
            st.warning("No report data available.")


def display_analysis_error(error_message: str):
    """
    Display analysis error message

    Args:
        error_message: Error message string
    """
    st.error(f"❌ Analysis Error: {error_message}")

    st.markdown("""
    **Troubleshooting:**
    - Ensure the feedback batch exists
    - Check if the API server is running
    - Try analyzing a smaller dataset
    - Check the system logs for details
    """)


def display_loading_stages(stage: str = "Initializing"):
    """
    Display analysis loading stages

    Args:
        stage: Current processing stage
    """
    stages = {
        "Initializing": 0,
        "Data Ingestion": 25,
        "Sentiment Analysis": 50,
        "Topic Modeling": 75,
        "Synthesis": 90,
        "Complete": 100
    }

    progress = stages.get(stage, 0)

    st.progress(progress / 100)
    st.caption(f"**Current Stage:** {stage}")


def create_download_section(analysis_results: Dict[str, Any], feedback_id: str):
    """
    Create download section for results

    Args:
        analysis_results: Analysis results
        feedback_id: Feedback batch ID
    """
    st.markdown("---")
    st.subheader("📥 Download Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        # JSON download
        import json
        json_str = json.dumps(analysis_results, indent=2)

        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"analysis_{feedback_id}.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        # CSV download placeholder (will be implemented with exporters)
        st.button(
            "📊 Export to CSV",
            use_container_width=True,
            disabled=True,
            help="CSV export coming soon"
        )

    with col3:
        # PDF download placeholder
        st.button(
            "📑 Generate PDF",
            use_container_width=True,
            disabled=True,
            help="PDF export coming soon"
        )
