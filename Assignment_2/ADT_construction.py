from __future__ import annotations
from typing import Any, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from math import log
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

    def recommend_games(self, liked_game: str, top_k: int = 5) -> list[str]:
        """Recommend at most top_k games based on users who liked the given game."""
        if liked_game not in self._vertices:
            return []

        game_vertex = self._vertices[liked_game]
        if game_vertex.kind != 'game':
            return []

        # Step 1: Find users who played this game
        users = [v for v in game_vertex.neighbours if v.kind == 'user']

        # Step 2: Count scores for other games
        score_map = {}

        for user in users:
            for other_game, weight in user.neighbours.items():
                if other_game.kind == 'game' and other_game.item != liked_game:
                    if other_game.item not in score_map:
                        score_map[other_game.item] = 0
                    # Use user-game edge weight as score (i.e., user's preference strength)
                    score_map[other_game.item] += weight

        # Step 3: Sort games by score and return top_k
        sorted_games = sorted(score_map.items(), key=lambda x: x[1], reverse=True)

        return [game for game, _ in sorted_games[:top_k]]


########################################################################################################################
########################################################################################################################
def load_graph(filename: str) -> GameGraph:
    """Load user-game data from a filtered JSON file and return a GameGraph."""
    graph = GameGraph()

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())

                user_id = data['user_id']
                game_title = data['item_name']
                playtime = data.get('playtime_forever', 0)
                recommend = data.get('recommend', None)
                review = data.get('review', None)

                # 確保節點存在
                graph.add_vertex(user_id, kind='user')
                graph.add_vertex(game_title, kind='game')

                # 計算權重並加入邊
                weight = calculate_weight(playtime, recommend, review)
                graph.add_user_game_edge(user_id, game_title, weight)

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e} -- skipping line.")
            except Exception as e:
                print(f"Unexpected error: {e}, skipping line.")

    return graph


analyzer = SentimentIntensityAnalyzer()


def calculate_weight(playtime: int, recommend: Optional[bool] = None, review: Optional[str] = None) -> float:
    """Calculate the weight of a user-game edge externally."""
    weight = log(1 + playtime)

    if recommend is True:
        weight += 1.0
    elif recommend is False:
        weight -= 0.5

    if review:
        sentiment = analyzer.polarity_scores(review)['compound']
        weight += sentiment

    return max(weight, 0.0)
