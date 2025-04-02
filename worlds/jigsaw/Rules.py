import math
from collections import Counter, defaultdict
from typing import List, Optional

from BaseClasses import MultiWorld

from worlds.generic.Rules import set_rule


def add_piece(previous_solution, piece, nx, ny, added_piece_count):
    pieces_to_merge = set()
    if piece <= nx * (ny - 1):
        pieces_to_merge.add(piece + nx)
    if piece > nx:
        pieces_to_merge.add(piece - nx)
    if piece % nx != 1:
        pieces_to_merge.add(piece - 1)
    if piece % nx != 0:
        pieces_to_merge.add(piece + 1)
    
    merged_group = {piece}
    new_solution = []
    
    for group in previous_solution:
        if not pieces_to_merge.isdisjoint(group):
            merged_group.update(group)
        else:
            new_solution.append(group)
    
    new_solution.append(merged_group)
    return new_solution, added_piece_count + 1 - len(new_solution)


def get_merges_from_adding_piece(previous_solution, piece, nx, ny, added_piece_count):
    """add_piece, but without creating a new solution for better performance when a new solution is not needed."""
    pieces_to_merge = set()
    if piece <= nx * (ny - 1):
        pieces_to_merge.add(piece + nx)
    if piece > nx:
        pieces_to_merge.add(piece - nx)
    if piece % nx != 1:
        pieces_to_merge.add(piece - 1)
    if piece % nx != 0:
        pieces_to_merge.add(piece + 1)

    # Every group that does not intersect with `pieces_to_merge` will be a group in the new solution.
    # Every group that does intersect with `pieces_to_merge` will merge with `pieces_to_merge` to become a single group
    # in the new solution.
    # Iterating `previous_solution` and counting the number of groups is a hot loop. `sum` and `map` allow for both to
    # be performed in optimised C code. Only binding `pieces_to_merge.isdisjoint` once also helps a bit with
    # performance.
    new_solution_length = 1 + sum(map(pieces_to_merge.isdisjoint, previous_solution))
    return added_piece_count + 1 - new_solution_length


def remove_piece(previous_solution, piece, nx, ny, added_piece_count):
    # Find the group in previous_solution that piece is in
    group_to_remove = None
    for group in previous_solution:
        if piece in group:
            group_to_remove = group
            break
    
    if not group_to_remove:
        return previous_solution, added_piece_count - len(previous_solution)  # Piece not found in any group
    
    # Remove piece from that group and then remove that group in total (but keep it in memory)
    group_to_remove.remove(piece)
    previous_solution.remove(group_to_remove)
    
    # Re-add the remaining pieces in the removed group
    partial_solution = []
    for partial_piece_count, remaining_piece in enumerate(group_to_remove):
        partial_solution, _ = add_piece(partial_solution, remaining_piece, nx, ny, partial_piece_count)
    
    new_solution = previous_solution + partial_solution
    
    return new_solution, added_piece_count - 1 - len(new_solution)