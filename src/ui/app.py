"""
CLARA NLP - Main Streamlit Application
Multi-Agent Feedback Analysis System UI
"""

import streamlit as st
from src.ui.utils.session_state import initialize_session_state
from src.ui.utils.auth import init_session_state as init_auth_state, is_authenticated


# Page configuration
st.set_page_config(
    page_title="CLARA NLP - Feedback Analysis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "CLARA NLP - Multi-Agent NLP Feedback Analysis System v1.0.0"
    }
)

# Initialize session state
initialize_session_state()
init_auth_state()

# Custom CSS
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3rem;
        font-weight: 500;
    }

    /* Success/Error boxes */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 5px;
    }

    /* Dataframe styling */
    .dataframe {
        font-size: 0.9rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F5F5F5;
    }

    /* Headers */
    h1, h2, h3 {
        color: #1E88E5;
    }

    /* Remove extra padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">🤖 CLARA NLP</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Multi-Agent Feedback Analysis System</div>', unsafe_allow_html=True)

# Authentication status
if is_authenticated():
    user_info = st.session_state.get("user_info", {})
    st.success(f"✅ Logged in as **{user_info.get('username', 'User')}**")
else:
    st.warning("⚠️ You are not logged in. Please login to access all features.")
    st.info("👉 Navigate to the **🔐 Login** page from the sidebar to sign in")

st.markdown("---")

# Main content
st.markdown("""
### Welcome to CLARA NLP!

This is a production-grade NLP system for analyzing customer feedback, reviews, and survey responses.

**Key Features:**
- 📤 **Upload Feedback**: Submit feedback via text, CSV, or JSON
- 🔍 **AI Analysis**: Advanced sentiment analysis and topic modeling
- 📊 **Visualizations**: Interactive charts and insights
- 🔎 **Search**: Semantic search and filtering
- 📥 **Export**: Download results as PDF or CSV

**Get Started:**
1. Navigate to the **Upload** page to submit feedback
2. Go to **Analysis** to process your data
3. View results in **Visualize** and **Dashboard**

Use the sidebar to navigate between pages.
""")

# Connection status
with st.sidebar:
    st.markdown("### System Status")

    # Check API connection
    try:
        api_client = st.session_state.api_client
        is_connected = api_client.check_connection()

        if is_connected:
            st.success("✅ API Connected")

            # Get health info
            try:
                health = api_client.get_health()
                st.caption(f"Embedding Service: {'✅' if health.get('embedding_service') == 'healthy' else '❌'}")
                st.caption(f"Vector Store: {'✅' if health.get('vector_store') == 'healthy' else '❌'}")
                st.caption(f"Documents: {health.get('document_count', 0):,}")
            except:
                pass
        else:
            st.error("❌ API Disconnected")
            st.caption("Make sure the API server is running on http://localhost:8000")

    except Exception as e:
        st.error("❌ Connection Error")
        st.caption(str(e))

    st.markdown("---")

    # Quick stats
    if st.session_state.uploaded_feedback_ids:
        st.markdown("### Quick Stats")
        st.metric("Uploaded Batches", len(st.session_state.uploaded_feedback_ids))

    if st.session_state.analysis_history:
        st.metric("Analyses Performed", len(st.session_state.analysis_history))

    st.markdown("---")

    # Navigation hint
    st.markdown("""
    ### Navigation
    Use the pages in the sidebar to:
    - 📊 View Dashboard
    - 📤 Upload Feedback
    - 🔍 Analyze Data
    - 📈 View Visualizations
    - 🔎 Search Feedback
    - ⚙️ System Info
    """)

# Footer
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("**Version:** 1.0.0")

with col2:
    st.caption("**Backend:** FastAPI + Multi-Agent System")

with col3:
    st.caption("**Powered by:** spaCy, VADER, BERTopic")

# Instructions for first-time users
if not st.session_state.uploaded_feedback_ids:
    st.info("""
    👋 **First time here?**

    Start by uploading some feedback data:
    1. Click **Upload** in the sidebar
    2. Choose your upload method (Text, CSV, or JSON)
    3. Submit your data
    4. Then head to **Analysis** to process it!
    """)
