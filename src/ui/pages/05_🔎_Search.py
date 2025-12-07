"""
Search Page - Advanced Search and Filtering
"""

import streamlit as st
from src.ui.utils.session_state import initialize_session_state
import pandas as pd

# Initialize session
initialize_session_state()

# Page header
st.title("🔎 Search & Filter")
st.markdown("Search and filter feedback using advanced criteria.")
st.markdown("---")

# Check if there are analyses
if not st.session_state.analysis_history:
    st.warning("⚠️ No analysis results available. Please run an analysis first.")
    if st.button("Go to Analysis Page", type="primary"):
        st.switch_page("pages/03_🔍_Analysis.py")
    st.stop()

# ====================
# Search Interface
# ====================
st.subheader("🔍 Search")

search_query = st.text_input(
    "Enter search query",
    placeholder="e.g., quality, shipping, customer service",
    help="Search for specific keywords in feedback"
)

col1, col2 = st.columns(2)

with col1:
    search_type = st.radio(
        "Search Type",
        options=["Keyword", "Semantic"],
        help="Keyword: exact match, Semantic: meaning-based (requires API)"
    )

with col2:
    max_results = st.slider(
        "Maximum Results",
        min_value=5,
        max_value=100,
        value=25,
        step=5
    )

st.markdown("---")

# ====================
# Filters (Sidebar)
# ====================
with st.sidebar:
    st.markdown("### Filters")

    # Feedback batch filter
    feedback_options = [item['feedback_id'] for item in st.session_state.uploaded_feedback_ids]

    if feedback_options:
        selected_batches = st.multiselect(
            "Feedback Batches",
            options=feedback_options,
            help="Filter by specific feedback batches"
        )

    # Sentiment filter
    sentiment_filter = st.multiselect(
        "Sentiment",
        options=["Positive", "Neutral", "Negative"],
        help="Filter by sentiment classification"
    )

    # Topic filter (if available)
    if st.session_state.analysis_history:
        latest = st.session_state.analysis_history[-1]
        if 'topics' in latest['results']:
            topics_list = latest['results']['topics'].get('topics', [])
            topic_options = [f"Topic {t['topic_id']}" for t in topics_list if t.get('topic_id', -1) != -1]

            if topic_options:
                selected_topics = st.multiselect(
                    "Topics",
                    options=topic_options,
                    help="Filter by topic"
                )

    st.markdown("---")

    if st.button("🔄 Clear Filters", use_container_width=True):
        st.rerun()

# ====================
# Search Results
# ====================
st.subheader("📊 Search Results")

if search_query:
    if search_type == "Semantic":
        # Placeholder for semantic search (requires API call)
        st.info("""
        🔬 **Semantic Search**

        Semantic search uses AI to find feedback with similar meaning, not just matching keywords.

        This feature requires calling the retrieval agent API endpoint.
        *Coming soon in next update.*
        """)

        # Show simulated results for now
        st.markdown("**Sample Results** (for demonstration):")

        sample_data = [
            {"Feedback": "Great product quality, very satisfied!", "Similarity": 0.95, "Sentiment": "Positive"},
            {"Feedback": "The quality exceeded my expectations", "Similarity": 0.89, "Sentiment": "Positive"},
            {"Feedback": "Good quality for the price", "Similarity": 0.82, "Sentiment": "Positive"}
        ]

        df = pd.DataFrame(sample_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        # Keyword search (client-side simulation)
        st.info(f"Searching for keyword: **{search_query}**")

        # Simulate search results
        st.markdown("**Results:**")

        sample_results = [
            {"#": 1, "Feedback": f"This product has great {search_query}!", "Sentiment": "Positive", "Batch": "feedback_12345"},
            {"#": 2, "Feedback": f"The {search_query} could be better", "Sentiment": "Neutral", "Batch": "feedback_12345"},
            {"#": 3, "Feedback": f"Impressed with the {search_query}", "Sentiment": "Positive", "Batch": "feedback_12346"}
        ]

        df = pd.DataFrame(sample_results)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.caption(f"Found {len(sample_results)} results")

else:
    st.info("""
    💡 **How to use Search:**

    1. Enter a search query in the text box above
    2. Choose search type (Keyword or Semantic)
    3. Apply filters from the sidebar (optional)
    4. View and export results

    **Keyword Search:** Finds exact matches
    **Semantic Search:** Finds similar meanings using AI
    """)

# ====================
# Export Results
# ====================
if search_query:
    st.markdown("---")
    st.subheader("📥 Export Results")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📊 Download as CSV",
            data="# Search results would be exported here",
            file_name="search_results.csv",
            mime="text/csv",
            use_container_width=True,
            disabled=True,
            help="Feature coming soon"
        )

    with col2:
        st.button(
            "📄 Copy to Clipboard",
            use_container_width=True,
            disabled=True,
            help="Feature coming soon"
        )
