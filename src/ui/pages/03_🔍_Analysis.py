"""
Analysis Page - Execute and View Analysis Results
"""

import streamlit as st
from src.ui.utils.session_state import initialize_session_state, add_analysis_result, get_feedback_list
from src.ui.components.result_displays import (
    display_complete_results,
    display_analysis_error,
    create_download_section
)
from src.ui.utils.formatters import format_timestamp, format_large_number

# Initialize session
initialize_session_state()

# Page header
st.title("🔍 Analysis")
st.markdown("Analyze uploaded feedback to extract emotions, topics, and insights.")
st.markdown("---")

# Check if there are uploaded feedback batches
feedback_list = get_feedback_list()

if not feedback_list:
    st.warning("⚠️ No feedback batches found. Please upload feedback first.")
    if st.button("Go to Upload Page", type="primary"):
        st.switch_page("pages/02_📤_Upload.py")
    st.stop()

# ====================
# SECTION 1: Select Feedback Batch
# ====================
st.subheader("1️⃣ Select Feedback Batch")

# Create options for selectbox
feedback_options = {}
for item in feedback_list:
    feedback_id = item['feedback_id']
    count = item['count']
    timestamp = format_timestamp(item['timestamp'], "%Y-%m-%d %H:%M")
    label = f"{feedback_id} ({count} items) - {timestamp}"
    feedback_options[label] = item

selected_label = st.selectbox(
    "Choose a feedback batch to analyze",
    options=list(feedback_options.keys()),
    help="Select from previously uploaded feedback batches"
)

selected_batch = feedback_options[selected_label]
feedback_id = selected_batch['feedback_id']

# Display batch info
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Feedback ID", feedback_id)

with col2:
    st.metric("Items", format_large_number(selected_batch['count']))

with col3:
    st.metric("Uploaded", format_timestamp(selected_batch['timestamp'], "%Y-%m-%d"))

st.markdown("---")

# ====================
# SECTION 2: Analysis Options
# ====================
st.subheader("2️⃣ Analysis Options")

col1, col2 = st.columns(2)

with col1:
    include_summary = st.checkbox(
        "Include Summary",
        value=True,
        help="Generate text summary using TextRank"
    )

    include_topics = st.checkbox(
        "Include Topics",
        value=True,
        help="Perform topic modeling with BERTopic"
    )

with col2:
    max_topics = st.slider(
        "Maximum Topics",
        min_value=1,
        max_value=20,
        value=10,
        help="Maximum number of topics to discover"
    )

# Advanced options
with st.expander("⚙️ Advanced Options"):
    col1, col2 = st.columns(2)

    with col1:
        min_topic_size = st.number_input(
            "Minimum Topic Size",
            min_value=2,
            max_value=50,
            value=5,
            help="Minimum number of documents per topic"
        )

    with col2:
        emotion_threshold = st.number_input(
            "Emotion Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.15,
            step=0.01,
            help="Minimum score to consider emotion present"
        )

# Build options dictionary
analysis_options = {
    'include_summary': include_summary,
    'include_topics': include_topics,
    'max_topics': max_topics,
    'min_topic_size': min_topic_size,
    'emotion_threshold': emotion_threshold
}

st.markdown("---")

# ====================
# SECTION 3: Execute Analysis
# ====================
st.subheader("3️⃣ Execute Analysis")

# Analyze button
if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
    try:
        api_client = st.session_state.api_client

        # Create progress placeholder
        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        with st.spinner("🔄 Analyzing feedback..."):
            # Show progress
            progress_placeholder.progress(0)
            status_placeholder.info("📊 Initializing analysis...")

            # Call API
            response = api_client.analyze_feedback(
                feedback_id=feedback_id,
                options=analysis_options
            )

            # Update progress
            progress_placeholder.progress(100)
            status_placeholder.success("✅ Analysis complete!")

            # Check response
            if response.get('success'):
                # Store results
                add_analysis_result(feedback_id, response)

                st.success("🎉 Analysis completed successfully!")
                st.balloons()

                # Set session state to display results
                st.session_state.current_analysis = response

            else:
                error_msg = response.get('error', 'Unknown error occurred')
                display_analysis_error(error_msg)

    except Exception as e:
        display_analysis_error(str(e))

st.markdown("---")

# ====================
# SECTION 4: Display Results
# ====================
if st.session_state.current_analysis:
    st.subheader("4️⃣ Analysis Results")

    results = st.session_state.current_analysis

    # Check if analysis was successful
    if results.get('success'):
        # Display complete results
        display_complete_results(results)

        # Download section
        create_download_section(results, results.get('feedback_id', feedback_id))

    else:
        st.error("Analysis did not complete successfully.")
        if 'error' in results:
            st.error(f"Error: {results['error']}")

elif st.session_state.analysis_history:
    # Show option to view previous analysis
    st.info("💡 **Tip:** Click 'Start Analysis' above to analyze the selected feedback batch.")

    # Option to view previous results
    if st.button("📋 View Previous Analysis Results"):
        if st.session_state.analysis_history:
            latest = st.session_state.analysis_history[-1]
            st.session_state.current_analysis = latest['results']
            st.rerun()

else:
    st.info("""
    ℹ️ **Ready to analyze!**

    Click the **Start Analysis** button above to begin processing your feedback.

    **What happens during analysis:**
    1. 📊 **Data Ingestion** - Validates and cleans feedback
    2. 😊 **Emotion Analysis** - Analyzes emotions using DistilRoBERTa
    3. 🏷️ **Topic Modeling** - Discovers themes using BERTopic
    4. 📝 **Synthesis** - Generates summary and insights using TextRank
    """)

# Footer
st.markdown("---")
st.caption("""
**Analysis powered by:**
- DistilRoBERTa Emotion Analysis (6 emotions)
- BERTopic Topic Modeling
- TextRank Summarization
- Multi-Agent Orchestration
""")
