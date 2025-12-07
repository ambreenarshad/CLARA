"""
Upload Handlers for Different Input Formats
"""

import streamlit as st
import pandas as pd
from typing import Tuple, List, Dict, Optional, Any
from src.ui.utils.validators import (
    validate_feedback_list,
    validate_csv_file,
    validate_json_file,
    extract_feedback_from_json,
    detect_feedback_column,
    check_file_size,
    sanitize_feedback
)


def handle_text_input(text_area_content: str) -> Tuple[List[str], List[Dict], Dict[str, Any]]:
    """
    Handle manual text input (line-by-line)

    Args:
        text_area_content: Text from text area

    Returns:
        (feedback_list, metadata_list, validation_results)
    """
    if not text_area_content or not text_area_content.strip():
        return [], [], {'valid': False, 'total_count': 0, 'valid_count': 0, 'invalid_count': 0, 'errors': [], 'duplicates': 0}

    # Split by newlines
    lines = text_area_content.split('\n')

    # Clean and filter
    feedback_list = [sanitize_feedback(line) for line in lines if line.strip()]

    # Validate
    validation_results = validate_feedback_list(feedback_list)

    # No metadata for manual text input
    metadata_list = [{} for _ in validation_results['valid_feedback']]

    return validation_results['valid_feedback'], metadata_list, validation_results


def handle_csv_upload(uploaded_file, encoding: str = 'utf-8') -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Handle CSV file upload and initial validation

    Args:
        uploaded_file: Streamlit UploadedFile object
        encoding: Character encoding

    Returns:
        (success, error_message, dataframe)
    """
    # Check file size
    file_size = uploaded_file.size
    size_valid, size_error = check_file_size(file_size)

    if not size_valid:
        return False, size_error, None

    # Read and validate CSV
    file_content = uploaded_file.getvalue()
    is_valid, error_msg, df = validate_csv_file(file_content, encoding)

    if not is_valid:
        return False, error_msg, None

    return True, "", df


def process_csv_data(
    df: pd.DataFrame,
    feedback_column: str,
    include_metadata: bool = True,
    metadata_columns: Optional[List[str]] = None
) -> Tuple[List[str], List[Dict], Dict[str, Any]]:
    """
    Process CSV DataFrame into feedback and metadata

    Args:
        df: CSV DataFrame
        feedback_column: Column containing feedback text
        include_metadata: Whether to include metadata
        metadata_columns: Specific columns to include as metadata (None = all except feedback)

    Returns:
        (feedback_list, metadata_list, validation_results)
    """
    # Extract feedback
    feedback_list = df[feedback_column].astype(str).tolist()

    # Sanitize
    feedback_list = [sanitize_feedback(text) for text in feedback_list]

    # Validate
    validation_results = validate_feedback_list(feedback_list)

    # Extract metadata
    metadata_list = []

    if include_metadata:
        # Determine metadata columns
        if metadata_columns is None:
            metadata_columns = [col for col in df.columns if col != feedback_column]

        # Extract metadata for valid feedback
        for feedback in validation_results['valid_feedback']:
            # Find row index
            try:
                idx = feedback_list.index(feedback)
                row = df.iloc[idx]

                metadata = {}
                for col in metadata_columns:
                    value = row[col]
                    # Convert to JSON-serializable types
                    if pd.isna(value):
                        continue
                    elif isinstance(value, (int, float, str, bool)):
                        metadata[col] = value
                    else:
                        metadata[col] = str(value)

                metadata_list.append(metadata)
            except:
                metadata_list.append({})
    else:
        metadata_list = [{} for _ in validation_results['valid_feedback']]

    return validation_results['valid_feedback'], metadata_list, validation_results


def handle_json_upload(uploaded_file, encoding: str = 'utf-8') -> Tuple[bool, str, Optional[List]]:
    """
    Handle JSON file upload and initial validation

    Args:
        uploaded_file: Streamlit UploadedFile object
        encoding: Character encoding

    Returns:
        (success, error_message, parsed_data)
    """
    # Check file size
    file_size = uploaded_file.size
    size_valid, size_error = check_file_size(file_size)

    if not size_valid:
        return False, size_error, None

    # Read and validate JSON
    file_content = uploaded_file.getvalue()
    is_valid, error_msg, data = validate_json_file(file_content, encoding)

    if not is_valid:
        return False, error_msg, None

    return True, "", data


def process_json_data(data: List[Any]) -> Tuple[List[str], List[Dict], Dict[str, Any]]:
    """
    Process JSON data into feedback and metadata

    Args:
        data: Parsed JSON list

    Returns:
        (feedback_list, metadata_list, validation_results)
    """
    # Extract feedback and metadata
    feedback_list, metadata_list = extract_feedback_from_json(data)

    # Sanitize
    feedback_list = [sanitize_feedback(text) for text in feedback_list]

    # Validate
    validation_results = validate_feedback_list(feedback_list)

    # Filter metadata to match valid feedback
    valid_feedback = validation_results['valid_feedback']
    filtered_metadata = []

    for feedback in valid_feedback:
        try:
            idx = feedback_list.index(feedback)
            filtered_metadata.append(metadata_list[idx])
        except:
            filtered_metadata.append({})

    return valid_feedback, filtered_metadata, validation_results


def display_validation_results(validation_results: Dict[str, Any]):
    """
    Display validation results in Streamlit

    Args:
        validation_results: Validation results dictionary
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Entries", validation_results['total_count'])

    with col2:
        st.metric("Valid", validation_results['valid_count'], delta=None)

    with col3:
        if validation_results['invalid_count'] > 0:
            st.metric("Invalid", validation_results['invalid_count'], delta=None, delta_color="inverse")
        else:
            st.metric("Invalid", 0)

    with col4:
        if validation_results['duplicates'] > 0:
            st.metric("Duplicates", validation_results['duplicates'], help="Duplicate entries (not removed)")
        else:
            st.metric("Duplicates", 0)

    # Show errors if any
    if validation_results['errors']:
        with st.expander(f"View {len(validation_results['errors'])} Validation Errors", expanded=False):
            for idx, text, error in validation_results['errors']:
                st.error(f"**Line {idx + 1}:** {error}")
                if text:
                    st.code(text, language=None)


def display_feedback_preview(
    feedback_list: List[str],
    metadata_list: Optional[List[Dict]] = None,
    max_preview: int = 10
):
    """
    Display preview of feedback data

    Args:
        feedback_list: List of feedback texts
        metadata_list: Optional list of metadata dictionaries
        max_preview: Maximum items to preview
    """
    st.subheader("Preview")

    preview_count = min(len(feedback_list), max_preview)

    if preview_count == 0:
        st.warning("No valid feedback to preview")
        return

    # Create preview DataFrame
    preview_data = {
        '#': list(range(1, preview_count + 1)),
        'Feedback': [feedback_list[i][:100] + "..." if len(feedback_list[i]) > 100 else feedback_list[i]
                     for i in range(preview_count)]
    }

    # Add metadata columns if available
    if metadata_list and metadata_list[0]:
        # Get all metadata keys
        all_keys = set()
        for meta in metadata_list[:preview_count]:
            all_keys.update(meta.keys())

        for key in sorted(all_keys):
            preview_data[key] = [metadata_list[i].get(key, '') for i in range(preview_count)]

    df = pd.DataFrame(preview_data)

    st.dataframe(df, use_container_width=True, hide_index=True)

    if len(feedback_list) > max_preview:
        st.info(f"Showing {max_preview} of {len(feedback_list)} entries")


def create_upload_summary(
    feedback_count: int,
    has_metadata: bool,
    metadata_fields: Optional[List[str]] = None
) -> str:
    """
    Create upload summary text

    Args:
        feedback_count: Number of feedback items
        has_metadata: Whether metadata is included
        metadata_fields: List of metadata field names

    Returns:
        Summary text
    """
    summary = f"**{feedback_count}** feedback item{'s' if feedback_count != 1 else ''} ready to upload"

    if has_metadata and metadata_fields:
        summary += f"\n\nMetadata fields: {', '.join(metadata_fields)}"

    return summary
