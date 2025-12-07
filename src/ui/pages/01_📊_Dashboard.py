"""
Dashboard Page - Overview and Quick Stats
"""

import streamlit as st
from src.ui.utils.session_state import initialize_session_state, get_feedback_list, get_latest_analysis
from src.ui.utils.formatters import format_timestamp, format_sentiment_label, format_sentiment_emoji
import pandas as pd

# Initialize session
initialize_session_state()

# Page header
st.title("📊 Dashboard")
st.markdown("Overview of your feedback analysis activities.")
st.markdown("---")

# Get data
feedback_list = get_feedback_list()
latest_analysis = get_latest_analysis()

# ====================
# Key Metrics Row
# ====================
st.subheader("📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_batches = len(feedback_list)
    st.metric("Feedback Batches", total_batches)

with col2:
    total_items = sum([item['count'] for item in feedback_list]) if feedback_list else 0
    st.metric("Total Feedback Items", f"{total_items:,}")

with col3:
    total_analyses = len(st.session_state.analysis_history)
    st.metric("Analyses Performed", total_analyses)

with col4:
    if latest_analysis and latest_analysis.get('results', {}).get('sentiment'):
        compound = latest_analysis['results']['sentiment'].get('average_compound', 0)
        emoji = format_sentiment_emoji(compound)
        label = format_sentiment_label(compound)
        st.metric("Latest Sentiment", f"{emoji} {label}")
    else:
        st.metric("Latest Sentiment", "N/A")

st.markdown("---")

# ====================
# Recent Activity
# ====================
st.subheader("📋 Recent Activity")

if feedback_list:
    # Create DataFrame from feedback list
    df_data = []
    for item in reversed(feedback_list[-10:]):  # Last 10 uploads
        df_data.append({
            'Feedback ID': item['feedback_id'],
            'Upload Date': format_timestamp(item['timestamp'], "%Y-%m-%d %H:%M"),
            'Items': item['count']
        })

    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No feedback uploaded yet. Start by uploading some feedback!")

st.markdown("---")

# ====================
# Analysis History
# ====================
if st.session_state.analysis_history:
    st.subheader("🔍 Recent Analyses")

    # Show last 5 analyses
    for analysis in reversed(st.session_state.analysis_history[-5:]):
        with st.expander(f"Analysis: {analysis['feedback_id']} - {format_timestamp(analysis['timestamp'], '%Y-%m-%d %H:%M')}"):
            results = analysis['results']

            col1, col2 = st.columns(2)

            with col1:
                if 'sentiment' in results:
                    sent = results['sentiment']
                    compound = sent.get('average_compound', 0)
                    st.markdown(f"**Sentiment:** {format_sentiment_emoji(compound)} {format_sentiment_label(compound)} ({compound:.2f})")

            with col2:
                if 'topics' in results:
                    num_topics = results['topics'].get('num_topics', 0)
                    st.markdown(f"**Topics:** {num_topics}")

            if st.button(f"View Full Results", key=f"view_{analysis['feedback_id']}"):
                st.session_state.current_analysis = results
                st.switch_page("pages/03_🔍_Analysis.py")

    st.markdown("---")

# ====================
# Quick Actions
# ====================
st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📤 Upload New Feedback", use_container_width=True):
        st.switch_page("pages/02_📤_Upload.py")

with col2:
    if st.button("🔍 Analyze Feedback", use_container_width=True):
        st.switch_page("pages/03_🔍_Analysis.py")

with col3:
    if st.button("⚙️ System Health", use_container_width=True):
        st.switch_page("pages/06_⚙️_System.py")

st.markdown("---")

# ====================
# System Overview (if data available)
# ====================
if latest_analysis:
    st.subheader("📊 Latest Analysis Summary")

    results = latest_analysis['results']

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Sentiment Distribution**")
        if 'sentiment' in results:
            dist = results['sentiment'].get('sentiment_distribution', {})
            st.success(f"😊 Positive: {dist.get('positive', 0)}")
            st.info(f"😐 Neutral: {dist.get('neutral', 0)}")
            st.error(f"😞 Negative: {dist.get('negative', 0)}")

    with col2:
        st.markdown("**Topic Overview**")
        if 'topics' in results:
            topics = results['topics'].get('topics', [])
            if topics:
                for topic in topics[:3]:  # Show top 3 topics
                    keywords = topic.get('keywords', [])[:3]
                    count = topic.get('count', 0)
                    st.caption(f"**Topic {topic['topic_id']}:** {', '.join(keywords)} ({count} docs)")
else:
    st.info("Run your first analysis to see insights here!")
