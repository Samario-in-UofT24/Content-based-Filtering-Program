"""
This is the core mechanism of recommendation based on filtered data.
"""
from math import log
from ADT_graph import _Vertex, load_graph_from_filtered_data, build_recommendation_graph
from ADT_tree import Tree, build_genre_tree

loaded_graph = load_graph_from_filtered_data('filtered_data.json')
loaded_genre_tree = build_genre_tree('classified_game_extraction.json')
loaded_vertices = loaded_graph.get_all_vertices()


def get_game_genres(game: str, genre_tree: Tree) -> list[str]:
    """Get the genre of a game by using the tree ADT"""
    return genre_tree.get_genres(game)


def filter_similar_genre_games(liked_game: str, users: list[_Vertex], genre_tree: Tree,
                               genre_cache: dict[str, list[str]]) -> tuple[dict[str, float], dict[str, int]]:
    """Keep the game with same genre with the input game. Then construct a score dict"""

    liked_game_genres = genre_cache.get(liked_game)
    if liked_game_genres is None:
        liked_game_genres = get_game_genres(liked_game, genre_tree)
        genre_cache[liked_game] = liked_game_genres

    score_map = {}
    game_user_count = {}

    for user in users:
        for other_game, weight in user.neighbours.items():
            if other_game.kind != 'game' or other_game.item == liked_game:
                continue

            if other_game.item not in genre_cache:
                genre_cache[other_game.item] = get_game_genres(other_game.item, genre_tree)
            other_game_genres = genre_cache[other_game.item]

            if not set(liked_game_genres) & set(other_game_genres):
                continue

            score_map[other_game.item] = score_map.get(other_game.item, 0) + weight
            game_user_count[other_game.item] = game_user_count.get(other_game.item, 0) + 1

    return score_map, game_user_count


def normalize_and_rank_scores(score_map: dict[str, float],
                              game_user_count: dict[str, int],
                              boost_factor: float = 1.5,
                              top_k: int = 15) -> tuple[list[str], dict[str, float]]:
    """Formalize the score for each game. Return the name of game recommended and their correspounding score"""

    for game in score_map:
        score_map[game] /= log(1 + game_user_count[game])
        score_map[game] *= boost_factor

    sorted_games = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    top_games = [game for game, _ in sorted_games[:top_k]]

    return top_games, score_map


def genre_aware_recommend(liked_game: str, top_k: int = 15,
                          genre_tree: Tree = None,
                          graph_vertices: dict[str, _Vertex] = None,
                          boost_factor: float = 1.5) -> tuple[list[str], dict[str, float]]:
    """Recommend the game with similar genres to input game combining with their score"""

    if genre_tree is None or graph_vertices is None:
        raise ValueError("genre_tree and graph_vertices must be non-empty")

    if liked_game not in graph_vertices or graph_vertices[liked_game].kind != 'game':
        return [], {}

    liked_game_genres = get_game_genres(liked_game, genre_tree)
    if not liked_game_genres:
        return [], {}

    game_vertex = graph_vertices[liked_game]
    users = [v for v in game_vertex.neighbours if v.kind == 'user']

    genre_cache = {}
    score_map, game_user_count = filter_similar_genre_games(
        liked_game, users, genre_tree, genre_cache
    )

    return normalize_and_rank_scores(score_map, game_user_count, boost_factor, top_k)


def recommend_and_visualize(liked_game: str,
                            top_k: int = 10,
                            genre_tree: Tree = loaded_genre_tree,
                            boost_factor: float = 1.5) -> None:
    """
    Visualization and recommendation
    """
    graph_vertices = loaded_vertices

    # Step 1: Recommend and get games and their score
    recommended_games, score_map = genre_aware_recommend(
        liked_game,
        top_k=top_k,
        genre_tree=genre_tree,
        graph_vertices=graph_vertices,
        boost_factor=boost_factor
    )

    if not recommended_games:
        print(f'⚠️ No results：「{liked_game}」may not exist in the dataset or with unknown genre。')
        return

    # Step 1.5: Print recommendation list
    print(f"\n🎮 Based on『{liked_game}』, the Top-{top_k} game recommendation：\n")
    for i, game in enumerate(recommended_games, 1):
        print(f"{i}. {game} — Score: {score_map[game]:.3f}")

    # Step 2: Construct the graph with games only
    rec_graph = build_recommendation_graph(liked_game, score_map, recommended_games)

    # Step 3: Visualize the game-only graph
    rec_graph.visualize()
