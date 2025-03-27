import json
from ADT_tree import Tree


def build_genre_tree(path: str) -> Tree:
    """
    Read a JSON list and build genrr to game Tree.
    """

    root = Tree("All Games", [])

    with open(path, encoding="utf-8") as f:
        games = json.load(f)  # expects a JSON array

    for entry in games:
        game = entry["item_name"]
        for genre in entry["genre"]:
            root.insert_sequence([genre, game])

    return root


if __name__ == "__main__":
    tree = build_genre_tree("classified_games.json")
    print(tree.__str__())
