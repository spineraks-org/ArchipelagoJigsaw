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

    A board stores a cluster ID value for each piece placed on the board, where `None` indicates an empty space on the
    board.
    _0____3_
    ____4_3_
    __1_____
    __1_22__

    Piece placement behaviours:
    A)
    A newly placed piece that does not connect to any existing placed pieces is given a new unique cluster ID.
    _0____3_
    ____4_3_
    __1_____
    __1_22_5 <--

    B)
    A newly placed piece that connects to only a single piece gains the cluster ID of the connecting piece.
    _0____3_
    ____4_33 <--
    __1_____
    __1_22_5

    C)
    When a piece is placed that would connect to multiple existing clusters of pieces, the largest of the clusters is
    found and all pieces in the smaller clusters are added to the largest cluster.
    The cluster IDs of the smaller clusters can then be re-used later on.
    _0____3_     _0____3_
    ____4_33     ____4_33
    __1____X <-- __1____3 <--
    __1_22_5     __1_22_3 <--
    """

    # The puzzle board itself. A 1D list used to represent a 2D board.
    board: list[int | None]
    # A lookup of the adjacent pieces of each piece, used like a dict[int, tuple[int, ...]].
    adjacent_pieces: tuple[tuple[int, ...], ...]
    # The count of merged clusters of connected pieces.
    merges_count: int
    # cluster ID -> piece indices in the cluster.
    clusters: dict[int, list[int]]

    # Unused cluster IDs that newly added pieces can be assigned to if they do not merge into an existing cluster.
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
        self.clusters = {}

    def add_piece(self, piece_index: int):
        """
        Add a piece to the board.

        The behavior of attempting to add a piece which is already present in the board is undefined.
        """
        board = self.board

        # Get all adjacent cluster IDs.
        # Use incorrect typing to begin with because it is more efficient to remove `None` this way.
        found_clusters: set[int] = {board[connection] for connection in self.adjacent_pieces[piece_index]}  # type: ignore
        # Empty spaces on the board are set to `None`.
        found_clusters.discard(None)  # type: ignore

        num_adjacent_clusters = len(found_clusters)
        if num_adjacent_clusters == 0:
            # Isolated piece, give it a new ID
            new_id = self._unused_ids.pop()
            board[piece_index] = new_id
            self.clusters[new_id] = [piece_index]
        elif num_adjacent_clusters == 1:
            # Only one connecting cluster
            self.merges_count += 1
            found_cluster = next(iter(found_clusters))
            board[piece_index] = found_cluster
            self.clusters[found_cluster].append(piece_index)
        else:
            # Multiple connecting clusters
            self.merges_count += num_adjacent_clusters
            clusters = self.clusters

            clusters_iter = iter(found_clusters)

            first_cluster_id: int = next(clusters_iter)
            pieces_in_cluster = clusters[first_cluster_id]
            clusters_and_ids = [(first_cluster_id, pieces_in_cluster)]

            # Find the largest of the clusters
            largest_cluster_id = first_cluster_id
            largest_pieces_in_cluster = pieces_in_cluster
            largest_cluster_size = len(pieces_in_cluster)
            for cluster_id in clusters_iter:
                pieces_in_cluster = clusters[cluster_id]
                cluster_size = len(pieces_in_cluster)
                clusters_and_ids.append((cluster_id, pieces_in_cluster))
                if cluster_size > largest_cluster_size:
                    largest_cluster_size = cluster_size
                    largest_cluster_id = cluster_id
                    largest_pieces_in_cluster = pieces_in_cluster

            board[piece_index] = largest_cluster_id
            largest_pieces_in_cluster.append(piece_index)

            # Add the pieces in the smaller clusters into the largest cluster.
            unused_ids = self._unused_ids
            for cluster_id, pieces_in_cluster in clusters_and_ids:
                if pieces_in_cluster is largest_pieces_in_cluster:
                    continue
                largest_pieces_in_cluster.extend(pieces_in_cluster)
                del clusters[cluster_id]
                unused_ids.append(cluster_id)
                for piece_idx in pieces_in_cluster:
                    board[piece_idx] = largest_cluster_id

    def get_merges_from_adding_piece(self, piece_idx: int):
        """
        Get the number of merges that would be made by adding a piece.

        The behavior of attempting to get the number of merges from adding a piece which is already present in the board
        is undefined.
        """
        # Get all adjacent cluster IDs.
        board = self.board
        found_clusters = {board[connection] for connection in self.adjacent_pieces[piece_idx]}
        # Empty spaces on the board are set to `None`.
        return len(found_clusters) - 1 if None in found_clusters else len(found_clusters)

    def remove_piece(self, piece_idx: int):
        """
        Remove a piece from the board.

        This is more expensive than adding pieces and is more expensive the larger the group that the removed piece is
        in.
        """
        board = self.board
        cluster_id = board[piece_idx]
        assert cluster_id is not None, "Attempted to remove a piece that is not present in the board"
        # Remove the cluster this piece is in.
        pieces_in_cluster = self.clusters.pop(cluster_id)
        # The cluster ID is now unused, so give it back to the board.
        self._unused_ids.append(cluster_id)

        # Clear the space on the board where the cluster was
        for i in pieces_in_cluster:
            board[i] = None

        # Remove the piece that has been removed from the board.
        pieces_in_cluster.remove(piece_idx)

        # Reduce the total merges by the merges of the real cluster.
        # Note that `piece_idx` has already been removed from `pieces_in_cluster`.
        self.merges_count -= len(pieces_in_cluster)

        # Add all the pieces back on, besides the removed piece.
        add_piece = self.add_piece
        for i in pieces_in_cluster:
            add_piece(i)
