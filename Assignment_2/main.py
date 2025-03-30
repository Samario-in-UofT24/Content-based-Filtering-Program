"""
Main file for the Game Recommender System's Streamlit UI.
This file handles the main page of the application, allowing users to search for games
and receive personalized recommendations.
"""
import streamlit as st
from recommend_new import recommend_and_visualize
from steam_api import get_game_image_url, get_game_details


def featured_game() -> None:
    """
    Display detailed information about the top recommended game.
    """
    top_game = st.session_state['recommendations']['games'][0]
    if top_game:
        with st.spinner(f"Loading details for {top_game}..."):
            game_details = get_game_details(top_game)

        col1, col2 = st.columns(2)

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


def main() -> None:
    """
    Run the main Streamlit application for the game recommender system.
    """
    # initializing
    st.set_page_config(
        page_title="Ethan and Samario's Game Recommender System",
        page_icon="🎮",
        layout="wide"
    )

    # initialize session state for multi-page navigation
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []

    if 'cached_recommendations' not in st.session_state:
        st.session_state.cached_recommendations = {}

    st.title("Ethan and Samario's Game Recommender System")

    with st.sidebar:
        st.markdown("## Navigation")
        st.info("""
        - **Home**: Search for new recommendations
        - **Search History**: View your recent searches
        - **Visualization**: Explore game relationships
        """)

    # User input
    user_game = st.text_input("Enter the name of your favorite game:")
    search_button = st.button("Recommend Games")

    if user_game and search_button:
        st.write(f"Recommendations based on: **{user_game}**")
        st.write("Please be patient! (The first search may take a while)")

        # Add to search history if not already there
        if user_game not in st.session_state.search_history:
            st.session_state.search_history.append(user_game)
            # Keep only the last 10 searches
            if len(st.session_state.search_history) > 10:
                st.session_state.search_history = st.session_state.search_history[-10:]

        # Store the game name in session state
        st.session_state.favorite_game = user_game

        # The spinner
        with st.spinner("Generating game recommendations..."):
            recommended_games, score_map, genre_map = recommend_and_visualize(user_game, visualize=False)

            # Store recommendations in session state
            st.session_state.recommendations = {
                'games': recommended_games,
                'scores': score_map,
                'genres': genre_map
            }

            # Cache the results for reuse in history page
            st.session_state.cached_recommendations[user_game] = {
                'games': recommended_games,
                'scores': score_map,
                'genres': genre_map
            }

        if not recommended_games:
            st.error(f"No results: '{user_game}' may not exist in the dataset or has unknown genre.")
        else:
            # Display game images and information
            st.subheader("Recommended Games:")

            # Create 3 columns
            cols = st.columns(3)

            for i, game in enumerate(recommended_games[:6]):  # Show top 6 games
                with cols[i % 3]:
                    # Get game image from Steam API
                    st.image(get_game_image_url(game), caption=game, width=300)
                    st.write(f"**{game}**")
                    st.write(f"**Score:** {score_map[game]:.2f}")
                    st.write(f"**Genres:** {', '.join(genre_map.get(game, []))}")
                    st.markdown("---")

            st.empty()

            st.success("Recommendations generated successfully!")
            st.info("Go to the Visualization page in the sidebar to see game relationships!")

            # Display top recommended game
            st.markdown("---")
            st.subheader("Featured Game Details")
            featured_game()

    elif not user_game:
        st.warning("Please enter a game name.")


if __name__ == "__main__":
    import os
    import sys

    # Check for an environment variable that indicates we are already running via Streamlit.
    # Streamlit sets the STREAMLIT_RUN environment variable when launched via `-m streamlit run`.
    if "STREAMLIT_RUN" not in os.environ:
        # Relaunch using the streamlit runner.
        os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", __file__])
    else:
        main()
