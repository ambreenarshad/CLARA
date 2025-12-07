"""
Input Validation Utilities
"""

import re
import json
from typing import List, Tuple, Dict, Any
import pandas as pd
from io import StringIO


def validate_text_feedback(text: str, min_words: int = 3) -> Tuple[bool, str]:
    """
    Validate a single feedback text entry

    Args:
        text: Feedback text to validate
        min_words: Minimum number of words required

    Returns:
        (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Empty text"

    # Count words
    words = text.split()
    if len(words) < min_words:
        return False, f"Too short (minimum {min_words} words)"

    return True, ""


def validate_feedback_list(feedback_list: List[str], min_words: int = 3) -> Dict[str, Any]:
    """
    Validate a list of feedback texts

    Args:
        feedback_list: List of feedback strings
        min_words: Minimum words per feedback

    Returns:
        Dictionary with validation results:
        {
            'valid': bool,
            'total_count': int,
            'valid_count': int,
            'invalid_count': int,
            'errors': List[Tuple[int, str, str]],  # (index, text, error)
            'valid_feedback': List[str],
            'duplicates': int
        }
    """
    if not feedback_list:
        return {
            'valid': False,
            'total_count': 0,
            'valid_count': 0,
            'invalid_count': 0,
            'errors': [],
            'valid_feedback': [],
            'duplicates': 0
        }

    errors = []
    valid_feedback = []
    seen = set()
    duplicate_count = 0

    for idx, text in enumerate(feedback_list):
        is_valid, error_msg = validate_text_feedback(text, min_words)

        if not is_valid:
            errors.append((idx, text[:50] if text else "", error_msg))
        else:
            # Check for duplicates (warning, not blocking)
            if text.strip() in seen:
                duplicate_count += 1
            else:
                seen.add(text.strip())
            valid_feedback.append(text)

    return {
        'valid': len(valid_feedback) > 0,
        'total_count': len(feedback_list),
        'valid_count': len(valid_feedback),
        'invalid_count': len(errors),
        'errors': errors,
        'valid_feedback': valid_feedback,
        'duplicates': duplicate_count
    }


def validate_csv_file(file_content: bytes, encoding: str = 'utf-8') -> Tuple[bool, str, pd.DataFrame]:
    """
    Validate CSV file content

    Args:
        file_content: CSV file bytes
        encoding: Character encoding

    Returns:
        (is_valid, error_message, dataframe)
    """
    try:
        # Try to decode
        text_content = file_content.decode(encoding)

        # Try to parse as CSV
        df = pd.read_csv(StringIO(text_content))

        if df.empty:
            return False, "CSV file is empty", None

        if len(df.columns) == 0:
            return False, "No columns found in CSV", None

        return True, "", df

    except UnicodeDecodeError:
        return False, f"Unable to decode file with {encoding} encoding. Try a different encoding.", None
    except pd.errors.EmptyDataError:
        return False, "CSV file is empty or malformed", None
    except Exception as e:
        return False, f"CSV parsing error: {str(e)}", None


def detect_feedback_column(df: pd.DataFrame) -> str:
    """
    Detect which column likely contains feedback text

    Args:
        df: DataFrame from CSV

    Returns:
        Column name (or first column if detection fails)
    """
    # Common feedback column names
    feedback_keywords = [
        'feedback', 'comment', 'text', 'review', 'response',
        'message', 'content', 'description', 'note'
    ]

    # Check column names (case-insensitive)
    for col in df.columns:
        col_lower = str(col).lower()
        for keyword in feedback_keywords:
            if keyword in col_lower:
                return col

    # Fallback: find column with longest average text length
    text_lengths = {}
    for col in df.columns:
        try:
            avg_length = df[col].astype(str).str.len().mean()
            text_lengths[col] = avg_length
        except:
            continue

    if text_lengths:
        return max(text_lengths, key=text_lengths.get)

    # Final fallback: first column
    return df.columns[0]


def validate_json_file(file_content: bytes, encoding: str = 'utf-8') -> Tuple[bool, str, Any]:
    """
    Validate JSON file content

    Args:
        file_content: JSON file bytes
        encoding: Character encoding

    Returns:
        (is_valid, error_message, parsed_data)
    """
    try:
        # Try to decode
        text_content = file_content.decode(encoding)

        # Try to parse as JSON
        data = json.loads(text_content)

        # Check if it's a list
        if not isinstance(data, list):
            return False, "JSON must be a list (array)", None

        if len(data) == 0:
            return False, "JSON list is empty", None

        # Check if list items are strings or objects
        first_item = data[0]
        if not isinstance(first_item, (str, dict)):
            return False, "JSON list items must be strings or objects", None

        return True, "", data

    except UnicodeDecodeError:
        return False, f"Unable to decode file with {encoding} encoding", None
    except json.JSONDecodeError as e:
        return False, f"JSON parsing error: {str(e)}", None
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", None


def extract_feedback_from_json(data: List[Any]) -> Tuple[List[str], List[Dict]]:
    """
    Extract feedback texts and metadata from JSON data

    Args:
        data: Parsed JSON list (strings or objects)

    Returns:
        (feedback_list, metadata_list)
    """
    feedback_list = []
    metadata_list = []

    for item in data:
        if isinstance(item, str):
            # Simple string list
            feedback_list.append(item)
            metadata_list.append({})
        elif isinstance(item, dict):
            # Object list - try to find text field
            text = None
            metadata = item.copy()

            # Common text field names
            text_fields = ['text', 'feedback', 'comment', 'review', 'message', 'content']

            for field in text_fields:
                if field in item:
                    text = str(item[field])
                    metadata.pop(field, None)
                    break

            # Fallback: use first string value
            if text is None:
                for value in item.values():
                    if isinstance(value, str):
                        text = value
                        break

            if text:
                feedback_list.append(text)
                metadata_list.append(metadata)

    return feedback_list, metadata_list


def check_file_size(file_size_bytes: int, max_mb: int = 200) -> Tuple[bool, str]:
    """
    Check if file size is within limits

    Args:
        file_size_bytes: File size in bytes
        max_mb: Maximum size in megabytes

    Returns:
        (is_valid, error_message)
    """
    max_bytes = max_mb * 1024 * 1024

    if file_size_bytes > max_bytes:
        size_mb = file_size_bytes / (1024 * 1024)
        return False, f"File too large ({size_mb:.1f}MB). Maximum: {max_mb}MB"

    return True, ""


def sanitize_feedback(text: str) -> str:
    """
    Clean and sanitize feedback text

    Args:
        text: Raw feedback text

    Returns:
        Sanitized text
    """
    # Remove excessive whitespace
    text = ' '.join(text.split())

    # Remove null bytes
    text = text.replace('\x00', '')

    return text.strip()
