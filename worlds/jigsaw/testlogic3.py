# this very quickly script shows that the new logic is 10x faster when adding pieces one by one

import random
import cProfile

def N(pieces, nx, ny):  # old logic, calculate every instance anew
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
    return len(pieces) - len(all_groups)

def main():
    nx = 30
    ny = 30

    for n1 in range(1, 100):
        pieces = []
        for _ in range(nx * ny):
            r = random.randint(1, nx * ny)
            if r not in pieces:
                pieces.append(r)
                N(pieces, nx, ny)

# if __name__ == "__main__":
#     cProfile.run('main()')
    
def add_piece(previous_solution, piece, nx, ny):  # recalculate groups when one piece is added [[1,2], [8,9], [....]]
                                                    #  when I add 3 -> [[1,2,3,8,9], ...]
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
        if pieces_to_merge & set(group):
            merged_group.update(group)
        else:
            new_solution.append(group)
    
    new_solution.append(list(merged_group))
    previous_solution[:] = new_solution
    return previous_solution, sum(len(group) for group in previous_solution) - len(previous_solution)

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

def main2():
    nx = 30
    ny = 30

    for n1 in range(1, 100):
        pieces = []
        previous_solution = []
        for _ in range(nx * ny):
            r = random.randint(1, nx * ny)
            if random.random() < 0.9:
                if r not in pieces:
                    pieces.append(r)
                    previous_solution, a = add_piece(previous_solution, r, nx, ny)
            else:
                if r in pieces:
                    pieces.remove(r)
                    previous_solution, a = remove_piece(previous_solution, r, nx, ny)
            b = N(pieces, nx, ny)
            print(a,b)
            if a != b:
                exit()
                
# cProfile.run('main()')
# cProfile.run('main2()')
main2()
