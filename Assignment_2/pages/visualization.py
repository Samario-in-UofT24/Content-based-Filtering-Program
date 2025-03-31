"""
Visualization page for the Game Recommender System.
This file handles the visualization page of the application, showing graph-based visualizations
of game recommendations, genre distributions, and score comparisons.
"""
import streamlit as st
import plotly.express as px
from ADT_graph import build_recommendation_graph


def create_genre_distribution_chart(recommended_games: list, genre_map: dict) -> px.bar:
    """Create a bar chart showing the distribution of genres in recommended games.

    Args:
        recommended_games: A list of recommended game names
        genre_map: A dictionary mapping game names to their genres

    Returns:
        A plotly bar chart figure showing genre distribution
    """
    genre_counts = {}
    for game in recommended_games:
        for genre in genre_map.get(game, []):
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

    # Sort by frequency
    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)

    # the bar chart
    genres = [g[0] for g in sorted_genres]
    counts = [g[1] for g in sorted_genres]

    fig = px.bar(
        x=genres,
        y=counts,
        labels={'x': 'Genre', 'y': 'Count'},
        title='Genres in Recommended Games'
    )
    return fig


def create_score_comparison_chart(recommended_games: list, score_map: dict) -> px.bar:
    """Create a bar chart comparing recommendation scores for games.

    Args:
        recommended_games: A list of recommended game names
        score_map: A dictionary mapping game names to their recommendation scores

    Returns:
        A plotly bar chart figure showing score comparison
    """
    game_scores = []
    for game in recommended_games:
        game_scores.append({
            "Game": game,
            "Score": score_map.get(game, 0)
        })

    # Sort by score
    game_scores = sorted(game_scores, key=lambda x: x['Score'], reverse=True)

    # Create bar chart
    fig = px.bar(
        game_scores,
        x='Game',
        y='Score',
        title='Recommendation Scores'
    )
    return fig


st.set_page_config(
    page_title="Game Visualization",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Game Recommendation Visualization")

# Check if recommendations exist in session state
if 'recommendations' in st.session_state and 'favorite_game' in st.session_state:
    # Add sidebar navigation tips
    with st.sidebar:
        st.markdown("## Navigation")
        st.info("""
        - **Home**: Search for new recommendations
        - **Search History**: View your recent searches
        - **Visualization**: Explore game relationships
        """)

    st.write(f"Visualization for recommendations based on: **{st.session_state.favorite_game}**")

    recommendations = st.session_state.recommendations
    liked_game = st.session_state.favorite_game
    recommended_games = recommendations['games']
    score_map = recommendations['scores']
    genre_map = recommendations['genres']

    # Create visualization
    st.subheader("Game Relationship Graph")
    with st.spinner("Generating visualization..."):
        rec_graph = build_recommendation_graph(
            liked_game,
            score_map,
            recommended_games,
            genre_map
        )

        # the plotly figure
        fig = rec_graph.get_figure()
        st.plotly_chart(fig, use_container_width=True)

    # Additional visualizations
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Genre Distribution")
        genre_chart = create_genre_distribution_chart(recommended_games, genre_map)
        st.plotly_chart(genre_chart, use_container_width=True)

    with col2:
        st.subheader("Score Comparison")
        score_chart = create_score_comparison_chart(recommended_games, score_map)
        st.plotly_chart(score_chart, use_container_width=True)

else:
    st.warning("No recommendations found. Please go to the main page and search for a game first.")
    st.info("Click on the 'Game Recommender' link in the sidebar to go to the main page.")
