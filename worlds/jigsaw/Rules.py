import math
from collections import Counter, defaultdict
from typing import List, Optional

from BaseClasses import MultiWorld

from worlds.generic.Rules import set_rule


def set_jigsaw_rules(world: MultiWorld, player: int, nx: int, ny: int):
    """
    Sets rules on reaching matches
    """

    for location in world.get_locations(player):
        set_rule(
            location,
            lambda state, curmatches=location.nmatches, player=player: count_number_of_matches_state(
                state, player, nx, ny
            )
            >= curmatches,
        )
        
def count_number_of_matches_state(state, player, nx, ny):
    pieces = []
    for i in range(1, nx * ny + 1):
        if state.has(f"Puzzle Piece {i}", player):
            pieces.append(i)
    t = count_number_of_matches_pieces(pieces, nx, ny)
    return t
        
def count_number_of_matches_pieces(pieces, nx, ny):
    pieces_groups = []
    for p in pieces:
        pieces_groups.append([p])

    def is_match(p1, p2):
        if p2 < p1:
            return is_match(p2, p1)
        if p2 - p1 == 1 and p1 % nx != 0:
            return True
        if p2 - p1 == nx:
            return True
        return False

    def group_groups(pieces_groups):
        for i, group1 in enumerate(pieces_groups):
            for j, group2 in enumerate(pieces_groups[i+1:]):
                for p1 in group1:
                    for p2 in group2:
                        if is_match(p1, p2):
                            group1.extend(group2)
                            pieces_groups.remove(group2)
                            return True, pieces_groups
        return False, pieces_groups
                        
    while True:
        matched, pieces_groups = group_groups(pieces_groups)
        if not matched:
            break
        
    return len(pieces) - len(pieces_groups)