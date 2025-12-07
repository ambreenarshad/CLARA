"""
Session State Management for Streamlit UI
"""

import streamlit as st
from typing import Any, Dict, List, Optional
from datetime import datetime


def initialize_session_state():
    """
    Initialize session state variables if they don't exist
    """
    # API client instance
    if 'api_client' not in st.session_state:
        from src.ui.components.api_client import get_api_client
        st.session_state.api_client = get_api_client()

    # Uploaded feedback tracking
    if 'uploaded_feedback_ids' not in st.session_state:
        st.session_state.uploaded_feedback_ids = []

    # Analysis history: list of {feedback_id, timestamp, results, metadata}
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

    # Current analysis results
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None

    # Selected feedback ID
    if 'selected_feedback_id' not in st.session_state:
        st.session_state.selected_feedback_id = None

    # Upload data (temporary storage during upload process)
    if 'upload_data' not in st.session_state:
        st.session_state.upload_data = {
            'feedback': [],
            'metadata': [],
            'validated': False
        }

    # System statistics cache
    if 'system_stats' not in st.session_state:
        st.session_state.system_stats = None

    # Last statistics fetch time
    if 'last_stats_fetch' not in st.session_state:
        st.session_state.last_stats_fetch = None


def add_uploaded_feedback(feedback_id: str, count: int, timestamp: str = None):
    """
    Add a feedback ID to the uploaded list

    Args:
        feedback_id: Unique feedback batch ID
        count: Number of feedback items
        timestamp: Upload timestamp (defaults to now)
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    upload_record = {
        'feedback_id': feedback_id,
        'count': count,
        'timestamp': timestamp
    }

    st.session_state.uploaded_feedback_ids.append(upload_record)


def add_analysis_result(feedback_id: str, results: Dict[str, Any], metadata: Dict[str, Any] = None):
    """
    Add analysis results to history

    Args:
        feedback_id: Feedback batch ID
        results: Analysis results dictionary
        metadata: Additional metadata
    """
    analysis_record = {
        'feedback_id': feedback_id,
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'metadata': metadata or {}
    }

    # Add to history
    st.session_state.analysis_history.append(analysis_record)

    # Set as current analysis
    st.session_state.current_analysis = analysis_record


def get_analysis_by_feedback_id(feedback_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve analysis results for a specific feedback ID

    Args:
        feedback_id: Feedback batch ID

    Returns:
        Analysis record or None if not found
    """
    for analysis in reversed(st.session_state.analysis_history):
        if analysis['feedback_id'] == feedback_id:
            return analysis
    return None


def get_latest_analysis() -> Optional[Dict[str, Any]]:
    """
    Get the most recent analysis

    Returns:
        Latest analysis record or None
    """
    if st.session_state.analysis_history:
        return st.session_state.analysis_history[-1]
    return None


def clear_upload_data():
    """
    Clear temporary upload data
    """
    st.session_state.upload_data = {
        'feedback': [],
        'metadata': [],
        'validated': False
    }


def update_system_stats(stats: Dict[str, Any]):
    """
    Update cached system statistics

    Args:
        stats: System statistics dictionary
    """
    st.session_state.system_stats = stats
    st.session_state.last_stats_fetch = datetime.now()


def get_cached_stats(max_age_seconds: int = 30) -> Optional[Dict[str, Any]]:
    """
    Get cached system statistics if fresh enough

    Args:
        max_age_seconds: Maximum age of cache in seconds

    Returns:
        Cached stats or None if too old/not available
    """
    if st.session_state.system_stats is None:
        return None

    if st.session_state.last_stats_fetch is None:
        return None

    age = (datetime.now() - st.session_state.last_stats_fetch).total_seconds()

    if age <= max_age_seconds:
        return st.session_state.system_stats

    return None


def get_feedback_list() -> List[Dict[str, Any]]:
    """
    Get list of uploaded feedback batches

    Returns:
        List of upload records
    """
    return st.session_state.uploaded_feedback_ids


def get_analysis_count() -> int:
    """
    Get total number of analyses performed

    Returns:
        Count of analyses
    """
    return len(st.session_state.analysis_history)


def clear_all_data():
    """
    Clear all session state data (for reset/logout)
    """
    keys_to_clear = [
        'uploaded_feedback_ids',
        'analysis_history',
        'current_analysis',
        'selected_feedback_id',
        'upload_data',
        'system_stats',
        'last_stats_fetch'
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Reinitialize
    initialize_session_state()
