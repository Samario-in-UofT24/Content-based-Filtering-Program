"""
This is the core mechanism of recommendation based on filtered data.
"""
from math import log
import json
from ADT_graph import _Vertex, load_graph_from_filtered_data, build_recommendation_graph
from ADT_tree import Tree, build_genre_tree

# Load the game data for loading
with open('classified_game_extraction.json', encoding='utf-8') as f:
    GAMES_DATA = json.load(f)

LOADED_GRAPH = load_graph_from_filtered_data('filtered_data.json')
LOADED_GENRE_TREE = build_genre_tree(GAMES_DATA)
LOADED_VERTICES = LOADED_GRAPH.get_all_vertices()


def get_game_genres(game: str, genre_tree: Tree) -> list[str]:
    """Get the genre of a game by using the tree ADT"""
    return genre_tree.get_genres(game)


# def filter_similar_genre_games(liked_game: str, users: list[_Vertex], genre_tree: Tree,
#                                genre_cache: dict[str, list[str]]) \
#         -> tuple[dict[str, float], dict[str, int], dict[str, list[str]]]:
#     """Keep the game with same genre with the input game. Then construct a score dict"""

#     liked_game_genres = genre_cache.get(liked_game)
#     if liked_game_genres is None:
#         liked_game_genres = get_game_genres(liked_game, genre_tree)
#         genre_cache[liked_game] = liked_game_genres

#     score_map = {}
#     game_user_count = {}
#     genre_map = {}

#     for user in users:
#         for other_game, weight in user.neighbours.items():
#             if other_game.kind != 'game' or other_game.item == liked_game:
#                 continue

#             if other_game.item not in genre_cache:
#                 genre_cache[other_game.item] = get_game_genres(other_game.item, genre_tree)
#             other_game_genres = genre_cache[other_game.item]

#             if not set(liked_game_genres) & set(other_game_genres):
#                 continue

#             score_map[other_game.item] = score_map.get(other_game.item, 0) + weight
#             game_user_count[other_game.item] = game_user_count.get(other_game.item, 0) + 1
#             genre_map[other_game.item] = other_game_genres

#     return score_map, game_user_count, genre_map

# need to edit
def filter_similar_genre_games(liked_game: str,
                               users: list[_Vertex],
                               genre_tree: Tree,
                               genre_cache: dict[str, set]
                               ) -> tuple[dict[str, float], dict[str, int], dict[str, set]]:
    """
    Optimized filtering function that uses a precomputed genre mapping stored in a global variable.
    """
    # Use the globally cached precomputed genre map
    precomputed_genre_map = genre_tree.get_precomputed_genre_map()

    # Cache and convert liked game's genres to a set for efficient intersection.
    liked_game_genres = genre_cache.get(liked_game)
    if liked_game_genres is None:
        liked_game_genres = set(get_game_genres(liked_game, genre_tree))
        genre_cache[liked_game] = liked_game_genres

    score_map = {}
    game_user_count = {}

    # Iterate over each user and their neighbor games.
    for user in users:
        for other_game, weight in user.neighbours.items():
            if other_game.kind != 'game' or other_game.item == liked_game:
                continue

            # Retrieve the genres for the neighbor game from the precomputed mapping.
            other_game_genres = precomputed_genre_map.get(other_game.item, set())
            if not liked_game_genres.intersection(other_game_genres):
                continue  # Skip if there are no genres in common.

            # Update the score and count for this game.
            score_map[other_game.item] = score_map.get(other_game.item, 0) + weight
            game_user_count[other_game.item] = game_user_count.get(other_game.item, 0) + 1

    return score_map, game_user_count, precomputed_genre_map


def normalize_and_rank_scores(score_map: dict[str, float],
                              game_user_count: dict[str, int],
                              boost_factor: float = 1.5,
                              top_k: int = 15) -> tuple[list[str], dict[str, float]]:
    """Formalize the score for each game. Return the name of game recommended and their correspounding score"""

    for game in score_map:
        score_map[game] /= log(1 + game_user_count[game])
        score_map[game] *= boost_factor

    sorted_games = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    top_games = [g for g, _ in sorted_games[:top_k]]

    return top_games, score_map


# def genre_aware_recommend(liked_game: str, top_k: int = 15,
#                           genre_tree: Tree = None,
#                           graph_vertices: dict[str, _Vertex] = None,
#                           boost_factor: float = 1.5
#                           ) -> tuple[list[str], dict[str, float], dict[str, list[str]]]:
#     """
#     Recommend games similar to liked_game using genre filtering + user-game graph.

#     Returns:
#         - List of recommended game names (top_k)
#         - Dict mapping game -> score
#         - Dict mapping game -> genre list
#     """
#     if genre_tree is None or graph_vertices is None:
#         raise ValueError("genre_tree and graph_vertices must be provided.")

#     if liked_game not in graph_vertices or graph_vertices[liked_game].kind != 'game':
#         return [], {}, {}

#     liked_game_genres = get_game_genres(liked_game, genre_tree)
#     if not liked_game_genres:
#         return [], {}, {}

#     game_vertex = graph_vertices[liked_game]
#     users = [v for v in game_vertex.neighbours if v.kind == 'user']

#     genre_cache = {}
#     score_map, game_user_count, genre_map = filter_similar_genre_games(
#         liked_game, users, genre_tree, genre_cache
#     )

#     top_games, score_map = normalize_and_rank_scores(score_map, game_user_count, boost_factor, top_k)

#     return top_games, score_map, genre_map

# need to edit
def genre_aware_recommend(liked_game: str, top_k: int = 15,
                          genre_tree: Tree = None,
                          graph_vertices: dict[str, _Vertex] = None,
                          boost_factor: float = 1.5
                          ) -> tuple[list[str], dict[str, float], dict[str, list[str]]]:
    """
    Recommend games similar to liked_game using genre filtering + user-game graph.

    Returns:
        - List of recommended game names (top_k)
        - Dict mapping game -> score
        - Dict mapping game -> list of genres
    """

    if genre_tree is None or graph_vertices is None:
        raise ValueError("genre_tree and graph_vertices must be provided.")

    if liked_game not in graph_vertices or graph_vertices[liked_game].kind != 'game':
        return [], {}, {}

    liked_game_genres = get_game_genres(liked_game, genre_tree)
    if not liked_game_genres:
        return [], {}, {}

    game_vertex = graph_vertices[liked_game]
    users = [v for v in game_vertex.neighbours if v.kind == 'user']

    genre_cache: dict[str, set] = {}
    # Note: use the optimized filtering function.
    score_map, game_user_count, genre_map = filter_similar_genre_games(
        liked_game, users, genre_tree, genre_cache
    )

    top_games, score_map = normalize_and_rank_scores(score_map, game_user_count, boost_factor, top_k)

    # Convert the genre map from dict[str, set] to dict[str, list[str]] for the final output.
    genre_map_list = {game: list(genres) for game, genres in genre_map.items()}

    return top_games, score_map, genre_map_list


def recommend_and_visualize(liked_game: str,
                            top_k: int = 10,
                            genre_tree: Tree = LOADED_GENRE_TREE,
                            boost_factor: float = 1.5,
                            visualize: bool = True) -> tuple:
    """
    Visualization and recommendation.

    Args:
        liked_game: The game the user likes
        top_k: Number of recommendations to return
        genre_tree: The genre tree for genre-based filtering
        boost_factor: Factor to boost scores
        visualize: Whether to print recommendations and visualize graph

    Returns:
        Tuple of (recommended_games, score_map, genre_map)
    """
    graph_vertices = LOADED_VERTICES

    recommended_games, score_map, genre_map = genre_aware_recommend(
        liked_game,
        top_k=top_k,
        genre_tree=genre_tree,
        graph_vertices=graph_vertices,
        boost_factor=boost_factor
    )

    if not recommended_games:
        print(f'⚠️ No results: 「{liked_game}」 may not exist in the dataset or has unknown genre.')
        return [], {}, {}

    if visualize:
        print(f"\n🎮 Based on『{liked_game}』, the Top-{top_k} game recommendations:\n")
        for i, game in enumerate(recommended_games, 1):
            genres_str = ', '.join(genre_map.get(game, []))
            print(f"{i}. {game} — Score: {score_map[game]:.3f} | Genres: {genres_str}")

        rec_graph = build_recommendation_graph(liked_game, score_map, recommended_games, genre_map)
        rec_graph.visualize()

    return recommended_games, score_map, genre_map


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta

    python_ta.check_all(config={
        'extra-imports': [
            'math', 'json', 'networkx', 'plotly.graph_objects'
        ],
        'allowed-io': ['recommend_and_visualize'],
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'E9997', 'E9992']
    })
