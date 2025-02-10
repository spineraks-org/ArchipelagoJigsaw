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
    pieces = [int(m[13:]) for m in state.prog_items[player]]
    t = count_number_of_matches_pieces(pieces, nx, ny)
    return t
        
def count_number_of_matches_pieces(pieces, nx, ny):
    pieces_groups = group_groups(pieces, nx, ny)
    return len(pieces) - len(pieces_groups)

def group_groups(pieces, nx, ny):
    pieces_set = set(pieces)
    all_groups = []
    
    while pieces_set:
        current_group = [pieces_set.pop()]
        ind = 0
        
        while ind < len(current_group):
            piece = current_group[ind]
            ind += 1
            candidates = []
            if piece > nx:
                candidates.append(piece - nx)
            if piece <= nx * (ny - 1):
                candidates.append(piece + nx)
            if piece % nx != 1:
                candidates.append(piece - 1)
            if piece % nx != 0:
                candidates.append(piece + 1)
                
            for candidate in candidates:
                if candidate in pieces_set:
                    current_group.append(candidate)
                    pieces_set.remove(candidate)
        all_groups.append(current_group)
    return all_groups
