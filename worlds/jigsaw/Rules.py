import math
from collections import Counter, defaultdict
from typing import List, Optional

from BaseClasses import MultiWorld

from worlds.generic.Rules import set_rule


class PuzzleBoard:
    """
    Puzzle board implementation.

    Optimized for efficient adding pieces to the board and calculating the number of new merges that would be made when
    adding a piece.

    A board stores a group ID value for each piece placed on the board, where `None` indicates an empty space on the
    board.
    _0____3_
    ____4_3_
    __1_____
    __1_22__

    Piece placement behaviours:
    A)
    A newly placed piece that does not connect to any existing placed pieces is given a new unique group ID.
    _0____3_
    ____4_3_
    __1_____
    __1_22_5 <--

    B)
    A newly placed piece that connects to only a single group ID gains the group ID of the connecting piece.
    _0____3_
    ____4_33 <--
    __1_____
    __1_22_5

    C)
    When a piece is placed that would connect to multiple existing groups, the largest of the groups is found and all
    pieces in the smaller groups are added to the largest group.
    The group IDs of the smaller groups can then be re-used
    _0____3_     _0____3_
    ____4_33     ____4_33
    __1____X <-- __1____3 <--
    __1_22_5     __1_22_3 <--
    """

    # The puzzle board itself. A 1D list used to represent a 2D board.
    board: list[int | None]
    # A lookup of the adjacent pieces of each piece, used like a dict[int, tuple[int, ...]].
    adjacent_pieces: tuple[tuple[int, ...], ...]
    # The count of merged groups of connected pieces.
    merges_count: int
    # group ID -> piece indices in the group.
    groups: dict[int, list[int]]

    # Unused group IDs that newly added pieces can be assigned to if they do not merge into an existing group.
    _unused_ids: list[int]

    def __init__(self, width: int, height: int):
        pieces = range(width * height)
        # The maximum number of IDs that could be needed is the maximum number of isolated pieces possible, which is
        # half the number of spaces on the board when even, or half the number of spaces plus 1 when odd.
        max_isolated_pieces = len(pieces) // 2 + len(pieces) % 2
        self._unused_ids = list(range(max_isolated_pieces))
        self.board = [None] * len(pieces)

        # Pre-calculate the pieces that are adjacent to each piece.
        adjacent_pieces = []
        for i in pieces:
            piece_connections = []
            x = i % width
            y = i // width
            if x > 0:
                piece_connections.append(i - 1)
            if x < width - 1:
                piece_connections.append(i + 1)
            if y > 0:
                piece_connections.append(i - width)
            if y < height - 1:
                piece_connections.append(i + width)
            adjacent_pieces.append(tuple(piece_connections))
        self.adjacent_pieces = tuple(adjacent_pieces)
        self.merges_count = 0
        self.groups = {}

    def add_piece(self, piece_index: int):
        """
        Add a piece to the board.

        The behavior of attempting to add a piece which is already present in the board is undefined.
        """
        board = self.board

        # Get all adjacent group IDs.
        found_groups: set[int] = {board[connection] for connection in self.adjacent_pieces[piece_index]}  # type: ignore
        # Empty spaces on the board are set to `None`.
        found_groups.discard(None)  # type: ignore

        num_adjacent_groups = len(found_groups)
        if num_adjacent_groups == 0:
            # Isolated piece, give it a new ID
            new_id = self._unused_ids.pop()
            board[piece_index] = new_id
            self.groups[new_id] = [piece_index]
        elif num_adjacent_groups == 1:
            # Only one connecting group
            self.merges_count += 1
            found_group = next(iter(found_groups))
            board[piece_index] = found_group
            self.groups[found_group].append(piece_index)
        else:
            # Multiple connecting groups
            self.merges_count += num_adjacent_groups
            groups = self.groups

            groups_iter = iter(found_groups)

            first_group_id: int = next(groups_iter)
            pieces_in_group = groups[first_group_id]
            groups_and_ids = [(first_group_id, pieces_in_group)]

            # Find the largest of the groups
            largest_group_id = first_group_id
            largest_pieces_in_group = pieces_in_group
            largest_group_size = len(pieces_in_group)
            for group_id in groups_iter:
                pieces_in_group = groups[group_id]
                group_size = len(pieces_in_group)
                groups_and_ids.append((group_id, pieces_in_group))
                if group_size > largest_group_size:
                    largest_group_size = group_size
                    largest_group_id = group_id
                    largest_pieces_in_group = pieces_in_group

            board[piece_index] = largest_group_id
            largest_pieces_in_group.append(piece_index)

            # Add the pieces in the smaller groups into the largest group.
            unused_ids = self._unused_ids
            for group_id, pieces_in_group in groups_and_ids:
                if pieces_in_group is largest_pieces_in_group:
                    continue
                largest_pieces_in_group.extend(pieces_in_group)
                del groups[group_id]
                unused_ids.append(group_id)
                for piece_idx in pieces_in_group:
                    board[piece_idx] = largest_group_id

    def get_merges_from_adding_piece(self, piece_idx: int):
        """Get the number of merges that would be made by adding a piece."""
        # Get all adjacent group IDs.
        board = self.board
        found_groups = {board[connection] for connection in self.adjacent_pieces[piece_idx]}
        # Empty spaces on the board are set to `None`.
        return len(found_groups) - 1 if None in found_groups else len(found_groups)
