"""
Visualize Page - Interactive Charts and Visualizations
"""

import streamlit as st
from src.ui.utils.session_state import initialize_session_state
from src.ui.utils.formatters import get_all_emotion_colors, format_emotion_label
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
# Emotion Visualizations
# ====================
if 'emotions' in results:
    st.subheader("😊 Emotion Visualizations")

    emotion_data = results['emotions']
    distribution = emotion_data.get('emotion_distribution', {})
    average_scores = emotion_data.get('average_scores', {})
    dominant_emotion = emotion_data.get('dominant_emotion', 'neutral')

    # Get color mappings
    emotion_colors = get_all_emotion_colors()

    col1, col2 = st.columns(2)

    with col1:
        # Pie chart - Emotion Distribution
        st.markdown("**Emotion Distribution (by Count)**")

        labels = [format_emotion_label(e) for e in distribution.keys()]
        values = list(distribution.values())
        colors = [emotion_colors.get(e, '#9E9E9E') for e in distribution.keys()]

        fig_pie = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hole=0.3,
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])

        fig_pie.update_layout(
            height=400,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Bar chart - Average Emotion Scores
        st.markdown("**Average Emotion Scores**")

        emotions_list = list(average_scores.keys())
        scores_list = list(average_scores.values())
        colors_list = [emotion_colors.get(e, '#9E9E9E') for e in emotions_list]

        fig_bar = go.Figure(data=[
            go.Bar(
                x=[format_emotion_label(e) for e in emotions_list],
                y=scores_list,
                marker_color=colors_list,
                text=[f"{s:.1%}" for s in scores_list],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Score: %{y:.3f}<extra></extra>'
            )
        ])

        fig_bar.update_layout(
            yaxis_title="Average Score",
            height=400,
            yaxis=dict(range=[0, max(scores_list) * 1.2] if scores_list else [0, 1])
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    # Row 2: Emotion Diversity and Dominant Emotion
    col3, col4 = st.columns(2)

    with col3:
        # Dominant Emotion Highlight
        st.markdown("**Dominant Emotion**")

        dominant_color = emotion_colors.get(dominant_emotion, '#9E9E9E')
        dominant_label = format_emotion_label(dominant_emotion)
        dominant_count = distribution.get(dominant_emotion, 0)
        total_count = sum(distribution.values())
        dominant_pct = (dominant_count / total_count * 100) if total_count > 0 else 0

        st.markdown(
            f"""
            <div style="
                background-color: {dominant_color}20;
                border-left: 5px solid {dominant_color};
                padding: 20px;
                border-radius: 5px;
                text-align: center;
            ">
                <h2 style="color: {dominant_color}; margin: 0;">{dominant_label}</h2>
                <p style="font-size: 18px; margin: 5px 0;">
                    {dominant_count} feedbacks ({dominant_pct:.1f}%)
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        # Emotion Diversity Metric
        st.markdown("**Emotion Diversity**")

        diversity = emotion_data.get('emotion_diversity', 0)
        diversity_pct = diversity * 100

        # Color based on diversity level
        if diversity > 0.7:
            diversity_color = "#4CAF50"
            diversity_label = "High Diversity"
        elif diversity > 0.4:
            diversity_color = "#FF9800"
            diversity_label = "Moderate Diversity"
        else:
            diversity_color = "#2196F3"
            diversity_label = "Low Diversity"

        st.markdown(
            f"""
            <div style="
                background-color: {diversity_color}20;
                border-left: 5px solid {diversity_color};
                padding: 20px;
                border-radius: 5px;
                text-align: center;
            ">
                <h2 style="color: {diversity_color}; margin: 0;">{diversity:.2f}</h2>
                <p style="font-size: 18px; margin: 5px 0;">
                    {diversity_label}
                </p>
                <p style="font-size: 14px; color: #666; margin: 0;">
                    Emotional range across feedback
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

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
    if 'emotions' in results:
        dominant = results['emotions'].get('dominant_emotion', 'neutral')
        dominant_label = format_emotion_label(dominant)
        st.metric("Dominant Emotion", dominant_label)

with col2:
    if 'topics' in results:
        num_topics = results['topics'].get('num_topics', 0)
        st.metric("Topics Found", num_topics)

with col3:
    if 'emotions' in results:
        diversity = results['emotions'].get('emotion_diversity', 0)
        st.metric("Emotion Diversity", f"{diversity:.2f}")

# Footer
st.markdown("---")
st.info("""
💡 **Visualization Tips:**
- Hover over charts for detailed information
- Use the topic selector to explore different topics
- Download charts using the camera icon in the top-right corner of each chart
""")
