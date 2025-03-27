from __future__ import annotations
from typing import Any, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from math import log, sqrt
from collections import defaultdict
import json


class _Vertex:
    """A vertex in the game graph, representing either a user or a game."""
    item: Any
    kind: str  # 'user' or 'game'
    neighbours: dict['_Vertex', float]  # neighbour vertex -> edge weight

    def __init__(self, item: Any, kind: str) -> None:
        self.item = item
        self.kind = kind
        self.neighbours = {}

    def add_neighbour(self, neighbour: '_Vertex', weight: float = 1.0) -> None:
        """Add a neighbour with the given weight."""
        self.neighbours[neighbour] = weight


class GameGraph:
    """Graph ADT for the game recommendation system."""
    _vertices: dict[Any, _Vertex]  # item -> _Vertex

    def __init__(self) -> None:
        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a new vertex to the graph if it doesn't already exist."""
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, kind)

    def add_user_game_edge(self, item1: Any, item2: Any, weight: float = 1.0) -> None:
        """Add a weighted edge between two vertices (both directions)."""
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            v1.add_neighbour(v2, weight)
            v2.add_neighbour(v1, weight)

    def get_all_vertices(self) -> dict[Any, _Vertex]:
        """Return all vertices in the graph."""
        return self._vertices

    def recommend_games(self, liked_game: str, top_k: int = 5) -> list[str]:
        """
        This is the version of recommendation without the filtration of tree
        """
        if liked_game not in self._vertices or self._vertices[liked_game].kind != 'game':
            return []

        game_vertex = self._vertices[liked_game]
        users = [v for v in game_vertex.neighbours if v.kind == 'user']

        score_map = {}
        game_user_count = {}

        for user in users:
            for other_game, weight in user.neighbours.items():
                if other_game.kind == 'game' and other_game.item != liked_game:
                    score_map[other_game.item] = score_map.get(other_game.item, 0) + weight
                    game_user_count[other_game.item] = game_user_count.get(other_game.item, 0) + 1

        for game in score_map:
            # Lower the weight of frequent game with high popularity
            score_map[game] /= log(1 + game_user_count[game])

        sorted_games = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
        return [game for game, _ in sorted_games[:top_k]]


########################################################################################################################
########################################################################################################################
def compute_playtime_stats(filtered_data_file: str) -> dict[str, tuple[float, float]]:
    """從 filtered data 文件中讀取數據，返回每個遊戲的 (平均遊玩時長, 標準差)。

    返回值是一個字典：
        - key: 遊戲名稱 (str)
        - value: (平均值, 標準差) 的 tuple
    """
    game_playtimes = defaultdict(list)

    with open(filtered_data_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                game = data['item_name']
                playtime = data.get('playtime_forever', 0)
                game_playtimes[game].append(playtime)
            except (json.JSONDecodeError, KeyError, TypeError):
                continue  # 跳過錯誤行

    stats = {}
    for game, times in game_playtimes.items():
        if times:
            mean = sum(times) / len(times)
            variance = sum((t - mean) ** 2 for t in times) / len(times)
            std_dev = sqrt(variance)
            stats[game] = (mean, std_dev)

    return stats


def load_graph_from_filtered_data(filtered_data_file: str) -> GameGraph:
    """從 filtered data 文件中構建 GameGraph。

    - 添加 user 和 game 為 vertex
    - 根據 playtime / recommend / review 計算 user-game edge 的權重
    """
    graph = GameGraph()
    analyzer = SentimentIntensityAnalyzer()
    stats = compute_playtime_stats(filtered_data_file)  # 遊戲的 playtime mean/std

    with open(filtered_data_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                user = data['user_id']
                game = data['item_name']
                playtime = data.get('playtime_forever', 0)
                recommend = data.get('recommend', None)
                review = data.get('review', None)

                mean, std = stats.get(game, (0.0, 0.0))

                weight = calculate_weight(
                    playtime=playtime,
                    mean=mean,
                    std=std,
                    recommend=recommend,
                    review=review,
                    analyzer=analyzer
                )

                graph.add_vertex(user, kind='user')
                graph.add_vertex(game, kind='game')
                graph.add_user_game_edge(user, game, weight)

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Skipping line due to error: {e}")
                continue

    return graph


def calculate_weight(playtime: int,
                     mean: float,
                     std: float,
                     recommend: Optional[bool] = None,
                     review: Optional[str] = None,
                     analyzer: Optional[SentimentIntensityAnalyzer] = None) -> float:
    """Calculate a normalized weight for a user-game edge.

    Parameters:
        - playtime: Total time played for the game by this user.
        - mean: Average playtime of this game among all users.
        - std: Standard deviation of playtime for this game.
        - recommend: Whether the user recommends the game.
        - review: Text review (optional).
        - analyzer: SentimentIntensityAnalyzer from VADER (optional).

    Returns:
        - A non-negative float as the edge weight.
    """

    # --------- 1. Playtime Z-score Normalization ----------
    if std == 0:
        z_score = 0.0
    else:
        z_score = (playtime - mean) / std

    playtime_score = 0.5 * z_score

    # --------- 2. Recommendation --------------------------
    recommend_score = 0.0
    if recommend is True:
        recommend_score = 2.0
    elif recommend is False:
        recommend_score = -0.5

    # --------- 3. Sentiment Score from Review -------------

    sentiment_score = 0.0
    if review and analyzer:
        sentiment_score = analyzer.polarity_scores(review)['compound']

    # --------- Final weight -------------------------------
    final_weight = playtime_score + recommend_score + sentiment_score

    return max(final_weight, 0.0)
