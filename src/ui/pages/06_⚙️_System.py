"""
System Page - Health Status and Configuration
"""

import streamlit as st
from src.ui.utils.session_state import initialize_session_state, update_system_stats, get_cached_stats
from src.ui.utils.formatters import format_large_number, format_timestamp
from datetime import datetime

# Initialize session
initialize_session_state()

# Page header
st.title("⚙️ System Health & Configuration")
st.markdown("Monitor system status and view configuration details.")
st.markdown("---")

# Auto-refresh toggle
col1, col2 = st.columns([3, 1])

with col2:
    auto_refresh = st.checkbox("Auto-refresh", value=False, help="Refresh every 10 seconds")

if auto_refresh:
    st.rerun()

# ====================
# Health Status
# ====================
st.subheader("🏥 Health Status")

try:
    api_client = st.session_state.api_client

    # Fetch health status
    with st.spinner("Checking system health..."):
        health = api_client.get_health()

    # Display status
    col1, col2, col3 = st.columns(3)

    with col1:
        status = health.get('status', 'unknown')
        if status == 'healthy':
            st.success(f"✅ **API Status:** {status.upper()}")
        else:
            st.error(f"❌ **API Status:** {status.upper()}")

    with col2:
        embed_status = health.get('embedding_service', 'unknown')
        if embed_status == 'healthy':
            st.success(f"✅ **Embeddings:** {embed_status.upper()}")
        else:
            st.warning(f"⚠️ **Embeddings:** {embed_status.upper()}")

    with col3:
        vector_status = health.get('vector_store', 'unknown')
        if vector_status == 'healthy':
            st.success(f"✅ **Vector Store:** {vector_status.upper()}")
        else:
            st.warning(f"⚠️ **Vector Store:** {vector_status.upper()}")

    # Document count
    doc_count = health.get('document_count', 0)
    st.metric("Total Documents in Vector Store", format_large_number(doc_count))

    # Last updated
    st.caption(f"Last checked: {format_timestamp(datetime.now().isoformat(), '%Y-%m-%d %H:%M:%S')}")

except Exception as e:
    st.error(f"❌ Unable to connect to API: {str(e)}")
    st.markdown("""
    **Troubleshooting:**
    - Ensure the API server is running on http://localhost:8000
    - Check if all dependencies are installed
    - Verify network connectivity
    """)

st.markdown("---")

# ====================
# System Statistics
# ====================
st.subheader("📊 System Statistics")

try:
    # Try to get cached stats first
    stats = get_cached_stats(max_age_seconds=60)

    if stats is None:
        # Fetch fresh stats
        with st.spinner("Fetching statistics..."):
            stats = api_client.get_statistics()
            update_system_stats(stats)

    # Display statistics
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Session Statistics**")
        st.metric("Uploaded Batches", len(st.session_state.uploaded_feedback_ids))
        st.metric("Analyses Performed", len(st.session_state.analysis_history))

    with col2:
        st.markdown("**Database Statistics**")
        if isinstance(stats, dict):
            total_docs = stats.get('total_documents', 0)
            st.metric("Total Documents", format_large_number(total_docs))
        else:
            st.caption("Statistics not available")

except Exception as e:
    st.warning(f"Unable to fetch statistics: {str(e)}")

st.markdown("---")

# ====================
# System Information
# ====================
st.subheader("ℹ️ System Information")

try:
    info = api_client.get_info()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**API Configuration**")
        st.code(f"""
Title: {info.get('title', 'N/A')}
Version: {info.get('version', 'N/A')}
Description: {info.get('description', 'N/A')}
        """, language="text")

    with col2:
        st.markdown("**Model Information**")
        if 'models' in info:
            models = info['models']
            st.code(f"""
Embedding Model: {models.get('embedding_model', 'N/A')}
spaCy Model: {models.get('spacy_model', 'N/A')}
Embedding Dimension: {models.get('embedding_dimension', 'N/A')}
            """, language="text")

    # ChromaDB info
    if 'chromadb' in info:
        st.markdown("**Vector Store Configuration**")
        chroma = info['chromadb']
        st.code(f"""
Collection: {chroma.get('collection_name', 'N/A')}
Persist Directory: {chroma.get('persist_directory', 'N/A')}
        """, language="text")

    # NLP Configuration
    if 'nlp_config' in info:
        st.markdown("**NLP Configuration**")
        nlp_config = info['nlp_config']
        st.code(f"""
Min Topic Size: {nlp_config.get('min_topic_size', 'N/A')}
Max Topics: {nlp_config.get('max_topics', 'N/A')}
Sentiment Threshold: {nlp_config.get('sentiment_threshold', 'N/A')}
Summary Ratio: {nlp_config.get('summary_ratio', 'N/A')}
        """, language="text")

except Exception as e:
    st.warning(f"Unable to fetch system information: {str(e)}")

st.markdown("---")

# ====================
# Actions
# ====================
st.subheader("🔧 Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Status", use_container_width=True):
        # Clear cache and refresh
        st.session_state.system_stats = None
        st.rerun()

with col2:
    if st.button("🗑️ Clear Session Data", use_container_width=True):
        if st.session_state.get('confirm_clear', False):
            from src.ui.utils.session_state import clear_all_data
            clear_all_data()
            st.success("Session data cleared!")
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("Click again to confirm")

with col3:
    if st.button("📊 View API Docs", use_container_width=True):
        st.markdown("[Open API Documentation](http://localhost:8000/docs)")

# Reset confirm state
if 'confirm_clear' in st.session_state and not st.button("Cancel Clear", key="cancel_clear"):
    if st.session_state.confirm_clear:
        st.session_state.confirm_clear = False

st.markdown("---")

# ====================
# Connection Info
# ====================
st.subheader("🔌 Connection Information")

st.code(f"""
API Base URL: http://localhost:8000
Streamlit UI: http://localhost:8501

API Endpoints:
- Health: GET /health
- Info: GET /info
- Upload: POST /api/v1/upload
- Analyze: POST /api/v1/analyze
- Process: POST /api/v1/process
- Statistics: GET /api/v1/statistics
""", language="text")

# Footer
st.markdown("---")
st.caption("CLARA NLP v1.0.0 - Multi-Agent Feedback Analysis System")
