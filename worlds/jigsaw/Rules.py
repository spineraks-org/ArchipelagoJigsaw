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

    The pieces in each group are not tracked because this makes adding pieces more expensive, this makes piece removal
    more expensive, however, the removal of pieces is not expected to occur often.

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
    When a piece is placed that would connect to multiple existing groups, one way to handle this is to set all the
    pieces in those groups to the group ID of the largest group.
    _0____3_     _0____3_
    ____4_33     ____4_33
    __1____X <-- __1____3 <--
    __1_22_5     __1_22_3 <--
    However, this gets expensive to do as the groups get larger. Instead, a dictionary is used that maps each group ID
    already on the board to a 'real' group ID:
    _0____3_     _0____3_
    ____4_33     ____4_33
    __1____X <-- __1____3 <--
    __1_22_5     __1_22_5
    group_to_real_group[5] = 3
    real_group_to_groups[3].append(5)
    This means that other operations that need to check what group a piece is in need to get the group ID as stored on
    the board, but then look up the real group ID with `real_group_id = group_to_real_group[group_id_from_board]`.
    """

    # The puzzle board itself. A 1D list used to represent a 2D board.
    board: list[int | None]
    # A lookup of the adjacent pieces of each piece, used like a dict[int, tuple[int, ...]].
    adjacent_pieces: tuple[tuple[int, ...], ...]
    # The count of merged groups of connected pieces.
    merges_count: int
    # group ID -> real group ID, used like a dict[int, int]
    group_to_real_group: list[int]
    # real group ID -> group IDs mapped to this real group ID
    real_group_to_groups: dict[int, list[int]]

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
        self.group_to_real_group = [-1] * len(self._unused_ids)
        self.real_group_to_groups = {}

    def add_piece(self, piece_index: int):
        """
        Add a piece to the board.

        The behavior of attempting to add a piece which is already present in the board is undefined.
        """
        board = self.board

        # Get all adjacent group IDs.
        found_groups = {board[connection] for connection in self.adjacent_pieces[piece_index]}
        # Empty spaces on the board are set to `None`.
        found_groups.discard(None)

        num_adjacent_groups = len(found_groups)
        if num_adjacent_groups == 0:
            # Isolated piece, give it a new ID
            new_id = self._unused_ids.pop()
            board[piece_index] = new_id
            self.group_to_real_group[new_id] = new_id
            self.real_group_to_groups[new_id] = [new_id]
        elif num_adjacent_groups == 1:
            # Only one connecting group
            self.merges_count += 1
            board[piece_index] = next(iter(found_groups))
        else:
            # Multiple connecting groups, determine the real groups.
            group_to_real_group = self.group_to_real_group
            real_groups = {group_to_real_group[found_group] for found_group in found_groups}
            num_real_groups = len(real_groups)
            self.merges_count += num_real_groups
            if num_real_groups == 1:
                board[piece_index] = next(iter(real_groups))
            else:
                # Pick the first real group as the new real group.
                real_groups_iter = iter(real_groups)
                new_real_group = next(real_groups_iter)
                board[piece_index] = new_real_group

                # Re-map all groups mapped to the remaining real groups to the new real group.
                real_group_to_groups = self.real_group_to_groups
                groups_mapped_to_real_group = real_group_to_groups[new_real_group]
                for other_real_group in real_groups_iter:
                    groups = real_group_to_groups[other_real_group]
                    groups_mapped_to_real_group.extend(groups)
                    del real_group_to_groups[other_real_group]
                    for g in groups:
                        group_to_real_group[g] = new_real_group

    def get_merges_from_adding_piece(self, piece_idx: int):
        """Get the number of merges that would be made by adding a piece."""

        # Get all adjacent group IDs.
        board = self.board
        found_groups = {board[connection] for connection in self.adjacent_pieces[piece_idx]}
        # Empty spaces on the board are set to `None`.
        found_groups.discard(None)

        num_found = len(found_groups)
        if num_found == 0:
            return 0
        elif num_found == 1:
            # Only one connecting group
            return 1
        else:
            # Multiple connecting groups, return the number of real groups.
            group_to_real_group = self.group_to_real_group
            return len({group_to_real_group[found_group] for found_group in found_groups})
