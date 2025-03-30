"""
History page for the Game Recommender System.
This file handles the search history page of the application, allowing users to view
their previous searches and access cached recommendations.
"""
import streamlit as st
from recommend_new import recommend_and_visualize
from steam_api import get_game_image_url, get_game_details


def featured_game() -> None:
    """Display detailed information about the top recommended game.
    """
    top_game = st.session_state['recommendations']['games'][0]
    if top_game:
        with st.spinner(f"Loading details for {top_game}..."):
            game_details = get_game_details(top_game)

        col1, col2 = st.columns([1, 2])

        with col1:  # the game image
            st.image(game_details.get("header_image", get_game_image_url(top_game)), 400)

        with col2:  # the game information
            st.subheader(game_details.get("name", top_game))

            if "description" in game_details and game_details["description"]:
                st.write(game_details["description"])
            else:
                st.write("No description available for this game.")

            if "developers" in game_details and game_details["developers"]:
                st.write(f"**Developers:** {', '.join(game_details['developers'])}")
            else:
                st.write("No developers available for this game.")

            if "publishers" in game_details and game_details["publishers"]:
                st.write(f"**Publishers:** {', '.join(game_details['publishers'])}")
            else:
                st.write("No publishers available for this game.")

            if "release_date" in game_details:
                st.write(f"**Release Date:** {game_details['release_date']}")
            else:
                st.write("No release date available for this game.")

            if "genres" in game_details and game_details["genres"]:
                st.write(f"**Steam Genres:** {', '.join(game_details['genres'])}")
            else:
                st.write("No genres available for this game.")


def show_game_recommendations(game: str) -> None:
    """Display recommendations for a specific game.

    Args:
        game: The name of the game to show recommendations for
    """
    st.session_state.favorite_game = game

    # Generate recommendations (from cache)
    with st.spinner(f"Getting recommendations for {game}..."):
        if ('cached_recommendations' in st.session_state and
                game in st.session_state.cached_recommendations):
            # Retrieve from cache
            data = st.session_state.cached_recommendations[game]
            recommended_games = data['games']
            score_map = data['scores']
            genre_map = data['genres']
        else:
            # Generate new recommendations
            recommended_games, score_map, genre_map = recommend_and_visualize(game, visualize=False)

            # Cache the results
            if 'cached_recommendations' not in st.session_state:
                st.session_state.cached_recommendations = {}
            st.session_state.cached_recommendations[game] = {
                'games': recommended_games,
                'scores': score_map,
                'genres': genre_map
            }

        # Store in the current recommendations slot
        st.session_state.recommendations = {
            'games': recommended_games,
            'scores': score_map,
            'genres': genre_map
        }

    # Display recommendations
    if not recommended_games:
        st.error(f"No results for '{game}'.")
    else:
        st.subheader(f"Recommendations for {game}")

        # Create columns for the recommendations
        rec_cols = st.columns(3)

        for j, rec_game in enumerate(recommended_games[:6]):
            with rec_cols[j % 3]:
                st.image(get_game_image_url(rec_game), width=200)
                st.write(f"**{rec_game}**")
                st.write(f"**Score:** {score_map[rec_game]:.2f}")
                st.write(f"**Genres:** {', '.join(genre_map.get(rec_game, []))}")
                st.markdown("---")

        # Display featured game details
        st.subheader("Featured Game Details")
        featured_game()


def app() -> None:
    """Run the search history page of the Streamlit application."""
    st.set_page_config(
        page_title="Search History - Game Recommender",
        page_icon="🎮",
        layout="wide"
    )

    st.title("Your Search History")

    with st.sidebar:
        st.markdown("## Navigation")
        st.info("""
        - **Home**: Search for new recommendations
        - **Search History**: View your recent searches
        - **Visualization**: Explore game relationships
        """)

    if 'search_history' not in st.session_state or not st.session_state.search_history:
        st.info("You haven't searched for any games yet. Go to the home page to start recommending games!")
    else:
        st.write("Here are your recent searches. Click on any game to see its recommendations again.")

        # Display search history
        cols = st.columns(3)

        for i, game in enumerate(st.session_state.search_history):
            with cols[i % 3]:
                st.markdown(f"**{i + 1}. {game}**")

                # show recommendation
                if st.button(f"Show Recommendations", key=f"history_{i}"):
                    show_game_recommendations(game)


# Call the app function
app()
