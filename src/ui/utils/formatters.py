"""
Data Formatting Utilities
"""

from datetime import datetime
from typing import Any, Union


def format_sentiment_score(score: float, decimal_places: int = 2) -> str:
    """
    Format sentiment score with fixed decimal places

    Args:
        score: Sentiment score
        decimal_places: Number of decimal places

    Returns:
        Formatted score string
    """
    return f"{score:.{decimal_places}f}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format value as percentage

    Args:
        value: Value (0-1 or 0-100)
        decimal_places: Number of decimal places

    Returns:
        Formatted percentage string
    """
    if value <= 1.0:
        value = value * 100

    return f"{value:.{decimal_places}f}%"


def format_large_number(num: Union[int, float]) -> str:
    """
    Format large number with commas

    Args:
        num: Number to format

    Returns:
        Formatted number string
    """
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"


def format_timestamp(timestamp: Union[str, datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp to readable string

    Args:
        timestamp: Timestamp (ISO string or datetime object)
        format_str: Output format string

    Returns:
        Formatted timestamp string
    """
    if isinstance(timestamp, str):
        try:
            # Parse ISO format
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            return timestamp
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        return str(timestamp)

    return dt.strftime(format_str)


def format_date_short(timestamp: Union[str, datetime]) -> str:
    """
    Format timestamp to short date

    Args:
        timestamp: Timestamp

    Returns:
        Short date string (YYYY-MM-DD)
    """
    return format_timestamp(timestamp, "%Y-%m-%d")


def format_time_ago(timestamp: Union[str, datetime]) -> str:
    """
    Format timestamp as relative time (e.g., "2 hours ago")

    Args:
        timestamp: Timestamp

    Returns:
        Relative time string
    """
    if isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            return timestamp
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        return str(timestamp)

    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    delta = now - dt

    seconds = delta.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def format_sentiment_label(compound_score: float, threshold: float = 0.05) -> str:
    """
    Get sentiment label from compound score

    Args:
        compound_score: VADER compound score (-1 to 1)
        threshold: Neutral threshold

    Returns:
        Sentiment label (Positive/Neutral/Negative)
    """
    if compound_score >= threshold:
        return "Positive"
    elif compound_score <= -threshold:
        return "Negative"
    else:
        return "Neutral"


def format_sentiment_emoji(compound_score: float, threshold: float = 0.05) -> str:
    """
    Get emoji representing sentiment

    Args:
        compound_score: VADER compound score
        threshold: Neutral threshold

    Returns:
        Emoji string
    """
    if compound_score >= threshold:
        return "😊"
    elif compound_score <= -threshold:
        return "😞"
    else:
        return "😐"


def format_sentiment_color(compound_score: float, threshold: float = 0.05) -> str:
    """
    Get color code for sentiment

    Args:
        compound_score: VADER compound score
        threshold: Neutral threshold

    Returns:
        Color hex code
    """
    if compound_score >= threshold:
        return "#43A047"  # Green
    elif compound_score <= -threshold:
        return "#E53935"  # Red
    else:
        return "#757575"  # Gray


def format_keywords_list(keywords: list, scores: list, max_keywords: int = 10) -> str:
    """
    Format keywords and scores as readable string

    Args:
        keywords: List of keywords
        scores: List of relevance scores
        max_keywords: Maximum keywords to show

    Returns:
        Formatted string
    """
    items = []
    for i, (keyword, score) in enumerate(zip(keywords[:max_keywords], scores[:max_keywords])):
        items.append(f"{keyword} ({score:.2f})")

    return ", ".join(items)


def format_bytes(size_bytes: int) -> str:
    """
    Format bytes to human-readable size

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to readable string

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def color_code_sentiment_html(value: float, threshold: float = 0.05) -> str:
    """
    Create HTML span with color-coded sentiment

    Args:
        value: Sentiment score
        threshold: Neutral threshold

    Returns:
        HTML string
    """
    color = format_sentiment_color(value, threshold)
    label = format_sentiment_label(value, threshold)
    emoji = format_sentiment_emoji(value, threshold)

    return f'<span style="color: {color}; font-weight: bold;">{emoji} {label} ({value:.2f})</span>'


def format_topic_label(topic_id: int, keywords: list) -> str:
    """
    Create readable topic label

    Args:
        topic_id: Topic ID (-1 for outliers)
        keywords: Top keywords for topic

    Returns:
        Topic label string
    """
    if topic_id == -1:
        return "Outliers / Noise"

    # Use top 3 keywords
    top_words = keywords[:3] if len(keywords) >= 3 else keywords

    return f"Topic {topic_id}: {', '.join(top_words)}"


# ===== EMOTION-SPECIFIC FORMATTERS =====

def format_emotion_label(emotion: str) -> str:
    """
    Format emotion label with proper capitalization

    Args:
        emotion: Emotion name (joy, sadness, anger, fear, surprise, neutral)

    Returns:
        Formatted emotion label
    """
    return emotion.capitalize()


def format_emotion_emoji(emotion: str) -> str:
    """
    Get emoji representing emotion

    Args:
        emotion: Emotion name

    Returns:
        Emoji string
    """
    emotion_emojis = {
        "joy": "😊",
        "sadness": "😢",
        "anger": "😠",
        "fear": "😨",
        "surprise": "😲",
        "neutral": "😐"
    }
    return emotion_emojis.get(emotion.lower(), "😐")


def format_emotion_color(emotion: str) -> str:
    """
    Get color code for emotion

    Args:
        emotion: Emotion name

    Returns:
        Color hex code
    """
    emotion_colors = {
        "joy": "#4CAF50",      # Green
        "sadness": "#2196F3",  # Blue
        "anger": "#F44336",    # Red
        "fear": "#9C27B0",     # Purple
        "surprise": "#FF9800", # Orange
        "neutral": "#9E9E9E"   # Gray
    }
    return emotion_colors.get(emotion.lower(), "#9E9E9E")


def format_emotion_with_emoji(emotion: str, score: float = None) -> str:
    """
    Format emotion with emoji and optional score

    Args:
        emotion: Emotion name
        score: Optional emotion score (0-1)

    Returns:
        Formatted string
    """
    emoji = format_emotion_emoji(emotion)
    label = format_emotion_label(emotion)

    if score is not None:
        return f"{emoji} {label} ({score:.2%})"
    return f"{emoji} {label}"


def color_code_emotion_html(emotion: str, score: float = None) -> str:
    """
    Create HTML span with color-coded emotion

    Args:
        emotion: Emotion name
        score: Optional emotion score

    Returns:
        HTML string
    """
    color = format_emotion_color(emotion)
    emoji = format_emotion_emoji(emotion)
    label = format_emotion_label(emotion)

    if score is not None:
        return f'<span style="color: {color}; font-weight: bold;">{emoji} {label} ({score:.1%})</span>'
    return f'<span style="color: {color}; font-weight: bold;">{emoji} {label}</span>'


def get_all_emotion_colors() -> dict:
    """
    Get all emotion color mappings

    Returns:
        Dict mapping emotion names to color codes
    """
    return {
        "joy": "#4CAF50",
        "sadness": "#2196F3",
        "anger": "#F44336",
        "fear": "#9C27B0",
        "surprise": "#FF9800",
        "neutral": "#9E9E9E"
    }


def get_all_emotion_emojis() -> dict:
    """
    Get all emotion emoji mappings

    Returns:
        Dict mapping emotion names to emojis
    """
    return {
        "joy": "😊",
        "sadness": "😢",
        "anger": "😠",
        "fear": "😨",
        "surprise": "😲",
        "neutral": "😐"
    }
