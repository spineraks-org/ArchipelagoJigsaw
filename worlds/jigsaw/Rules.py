import math
from collections import Counter, defaultdict
from typing import List, Optional

from BaseClasses import MultiWorld

from worlds.generic.Rules import set_rule


def add_piece(previous_solution, piece, nx, ny):
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
    return new_solution, sum(len(group) for group in new_solution) - len(new_solution)

def remove_piece(previous_solution, piece, nx, ny):
    # Find the group in previous_solution that piece is in
    group_to_remove = None
    for group in previous_solution:
        if piece in group:
            group_to_remove = group
            break
    
    if not group_to_remove:
        return previous_solution, sum(len(group) for group in previous_solution) - len(previous_solution)  # Piece not found in any group
    
    # Remove piece from that group and then remove that group in total (but keep it in memory)
    group_to_remove.remove(piece)
    previous_solution.remove(group_to_remove)
    
    # Re-add the remaining pieces in the removed group
    partial_solution = []
    for remaining_piece in group_to_remove:
        partial_solution, _ = add_piece(partial_solution, remaining_piece, nx, ny)
    
    new_solution = previous_solution + partial_solution
    
    return new_solution, sum(len(group) for group in new_solution) - len(new_solution)