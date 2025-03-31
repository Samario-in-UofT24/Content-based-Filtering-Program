"""
This file defines Tree ADT and related methods and helper functions. The Tree works as a filter in this assignment.
"""
from __future__ import annotations
from typing import Any, Optional


class Tree:
    """
    A recursive tree data structure.

    Note the relationship between this class and RecursiveList; the only major
    difference is that _rest has been replaced by _subtrees to handle multiple
    recursive sub-parts.

    Representation Invariants:
        - self._root is not None or self._subtrees == []
        - all(not subtree.is_empty() for subtree in self._subtrees)
    """
    # Private Instance Attributes:
    #   - _root:
    #       The item stored at this tree's root, or None if the tree is empty.
    #   - _subtrees:
    #       The list of subtrees of this tree. This attribute is empty when
    #       self._root is None (representing an empty tree). However, this attribute
    #       may be empty when self._root is not None, which represents a tree consisting
    #       of just one item.
    _root: Optional[Any]
    _subtrees: list[Tree]

    def __init__(self, root: Optional[Any], subtrees: list[Tree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

        Preconditions:
            - root is not none or subtrees == []
        """
        self._root = root
        self._subtrees = subtrees

    def is_empty(self) -> bool:
        """
        Return whether this tree is empty.
        """
        return self._root is None

    def __len__(self) -> int:
        """
        Return the number of items contained in this tree.
        """
        if self.is_empty():
            return 0
        else:
            size = 1  # count the root
            for subtree in self._subtrees:
                size += subtree.__len__()  # could also write len(subtree)
            return size

    def __contains__(self, item: Any) -> bool:
        """
        Return whether the given is in this tree.
        """
        if self.is_empty():
            return False
        elif self._root == item:
            return True
        else:
            for subtree in self._subtrees:
                if subtree.__contains__(item):
                    return True
            return False

    def __str__(self) -> str:
        """
        Return a string representation of this tree.

        For each node, its item is printed before any of its
        descendants' items. The output is nicely indented.

        You may find this method helpful for debugging.
        """
        return self._str_indented(0).rstrip()

    def _str_indented(self, depth: int) -> str:
        """
        Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            str_so_far = '  ' * depth + f'{self._root}\n'
            for subtree in self._subtrees:
                # Note that the 'depth' argument to the recursive call is
                # modified.
                str_so_far += subtree._str_indented(depth + 1)
            return str_so_far

    def _delete_root(self) -> None:
        """
        Remove the root item of this tree.

        Preconditions:
            - not self.is_empty()
        """
        if self._subtrees:
            self._root = None
        else:
            # Strategy: Promote a subtree (the rightmost one is chosen here).
            # Get the last subtree in this tree.
            last_subtree = self._subtrees.pop()

            self._root = last_subtree._root
            self._subtrees.extend(last_subtree._subtrees)

    def __repr__(self) -> str:
        """Return a one-line string representation of this tree.

        >>> t = Tree(2, [Tree(4, []), Tree(5, [])])
        >>> t
        Tree(2, [Tree(4, []), Tree(5, [])])
        """

        if self.is_empty():
            return 'Tree(None, [])'
        elif not self._subtrees:
            return f'Tree({self._root}, [])'
        else:
            return f'Tree({self._root}, {self._subtrees.__repr__()})'

    def insert_sequence(self, items: list) -> None:
        """
        Insert the given items into this tree.

        Preconditions:
            - not self.is_empty()

        """

        if not items:
            return

        for subtree in self._subtrees:
            if subtree._root == items[0]:
                subtree.insert_sequence(items[1:])
                return

        new_subtree = Tree(items[0], [])
        new_subtree.insert_sequence(items[1:])
        self._subtrees.append(new_subtree)

    def get_genres(self, game: str) -> list[str]:
        """
        Return every genre under which `game` appears.
        """
        if self.is_empty():
            return []

        genres = []

        for subtree in self._subtrees:
            if game in subtree:
                genres.append(subtree._root)
        return genres

    # need to edit
    def get_all_game_names(self) -> list[str]:
        """
        Return a list of all game names in the tree (filtering out genres).
        """

        if self.is_empty():
            return []

        # Assuming that a game node has no subtrees (or some other distinguishing property)
        if not self._subtrees:
            return [self._root]

        names = []
        for subtree in self._subtrees:
            names.extend(subtree.get_all_game_names())
        return names

    def get_precomputed_genre_map(self) -> dict[str, set]:
        """
        Compute and cache a mapping from each game name to its set of genres.
        This function will compute the map only once and reuse it in subsequent calls.
        """
        global _precomputed_genre_map
        if _precomputed_genre_map is None:
            _precomputed_genre_map = {}
            # Assumes your Tree class has a method get_all_game_names() to iterate over game names.
            for game in self.get_all_game_names():
                # Convert the list of genres to a set for fast intersection checks.
                _precomputed_genre_map[game] = set(self.get_genres(game))
        return _precomputed_genre_map


_precomputed_genre_map: Optional[dict[str, set]] = None


def build_genre_tree(data: list[dict]) -> Tree:
    """
    Construct a tree with games by genres。

    data: list of dictionaries. Includes {game name:genre}
    """
    root = Tree("All Games", [])

    for entry in data:
        game = entry["item_name"]
        for genre in entry["genre"]:
            root.insert_sequence([genre, game])

    return root


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['json', 'typing'],
        'allowed-io': [],
        'max-line-length': 120,
        'disable': ['C9104', 'E9992', 'E9997']
    })
