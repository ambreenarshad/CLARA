"""
Visualize Page - Interactive Charts and Visualizations
"""

import streamlit as st
from src.ui.utils.session_state import initialize_session_state
import plotly.graph_objects as go
import plotly.express as px

# Initialize session
initialize_session_state()

# Page header
st.title("📈 Visualizations")
st.markdown("Interactive charts and visual insights from your analysis.")
st.markdown("---")

# Check if there are any analyses
if not st.session_state.analysis_history:
    st.warning("⚠️ No analysis results found. Please run an analysis first.")
    if st.button("Go to Analysis Page", type="primary"):
        st.switch_page("pages/03_🔍_Analysis.py")
    st.stop()

# Select analysis to visualize
st.subheader("Select Analysis")

analysis_options = {}
for idx, analysis in enumerate(st.session_state.analysis_history):
    feedback_id = analysis['feedback_id']
    timestamp = analysis['timestamp']
    label = f"{feedback_id} - {timestamp[:19]}"
    analysis_options[label] = analysis

selected_label = st.selectbox(
    "Choose an analysis to visualize",
    options=list(analysis_options.keys())
)

selected_analysis = analysis_options[selected_label]
results = selected_analysis['results']

st.markdown("---")

# ====================
# Sentiment Visualizations
# ====================
if 'sentiment' in results:
    st.subheader("😊 Sentiment Visualizations")

    sentiment_data = results['sentiment']
    distribution = sentiment_data.get('sentiment_distribution', {})

    col1, col2 = st.columns(2)

    with col1:
        # Pie chart
        st.markdown("**Sentiment Distribution**")

        labels = ['Positive', 'Neutral', 'Negative']
        values = [
            distribution.get('positive', 0),
            distribution.get('neutral', 0),
            distribution.get('negative', 0)
        ]
        colors = ['#43A047', '#757575', '#E53935']

        fig_pie = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hole=0.3
        )])

        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Bar chart for scores
        st.markdown("**Sentiment Scores**")

        scores = {
            'Compound': sentiment_data.get('average_compound', 0),
            'Positive': sentiment_data.get('average_positive', 0),
            'Negative': sentiment_data.get('average_negative', 0),
            'Neutral': sentiment_data.get('average_neutral', 0)
        }

        fig_bar = go.Figure(data=[
            go.Bar(
                x=list(scores.keys()),
                y=list(scores.values()),
                marker_color=['#1E88E5', '#43A047', '#E53935', '#757575']
            )
        ])

        fig_bar.update_layout(
            yaxis_title="Score",
            height=400,
            yaxis=dict(range=[-1, 1])
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

# ====================
# Topic Visualizations
# ====================
if 'topics' in results:
    st.subheader("🏷️ Topic Visualizations")

    topics_data = results['topics']
    topics_list = topics_data.get('topics', [])

    if topics_list:
        # Filter out outlier topic
        topics_list = [t for t in topics_list if t.get('topic_id', -1) != -1]

        col1, col2 = st.columns(2)

        with col1:
            # Topic sizes bar chart
            st.markdown("**Topic Sizes**")

            topic_labels = [f"Topic {t['topic_id']}" for t in topics_list]
            topic_counts = [t.get('count', 0) for t in topics_list]

            fig_topics = go.Figure(data=[
                go.Bar(
                    x=topic_labels,
                    y=topic_counts,
                    marker_color='#1E88E5'
                )
            ])

            fig_topics.update_layout(
                yaxis_title="Document Count",
                height=400
            )

            st.plotly_chart(fig_topics, use_container_width=True)

        with col2:
            # Topic keywords
            st.markdown("**Top Keywords per Topic**")

            selected_topic_id = st.selectbox(
                "Select Topic",
                options=range(len(topics_list)),
                format_func=lambda x: f"Topic {topics_list[x]['topic_id']}"
            )

            selected_topic = topics_list[selected_topic_id]
            keywords = selected_topic.get('keywords', [])[:10]
            scores = selected_topic.get('scores', [])[:10]

            fig_keywords = go.Figure(data=[
                go.Bar(
                    y=keywords,
                    x=scores,
                    orientation='h',
                    marker_color='#FFA726'
                )
            ])

            fig_keywords.update_layout(
                xaxis_title="Relevance Score",
                height=400
            )

            st.plotly_chart(fig_keywords, use_container_width=True)

    else:
        st.info("No topics to visualize.")

    st.markdown("---")

# ====================
# Combined View
# ====================
st.subheader("📊 Combined Overview")

col1, col2, col3 = st.columns(3)

with col1:
    if 'sentiment' in results:
        compound = results['sentiment'].get('average_compound', 0)
        st.metric("Overall Sentiment", f"{compound:.3f}")

with col2:
    if 'topics' in results:
        num_topics = results['topics'].get('num_topics', 0)
        st.metric("Topics Found", num_topics)

with col3:
    if 'topics' in results:
        outliers = results['topics'].get('outliers', 0)
        st.metric("Outliers", outliers)

# Footer
st.markdown("---")
st.info("""
💡 **Visualization Tips:**
- Hover over charts for detailed information
- Use the topic selector to explore different topics
- Download charts using the camera icon in the top-right corner of each chart
""")
