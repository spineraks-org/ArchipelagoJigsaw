import random


nx = 600
ny = 600

# random.seed(1)
pieces = random.sample(range(1, nx * ny + 1), 300000)

def group_groups(pieces):
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
            if piece < nx * (ny - 1):
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

def group_groups2(pieces):
    pieces_set = set(pieces)
    
    parent = {i: i for i in pieces_set}
    
    def find(x):
        if x not in parent:
            return None
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        rootX = find(x)
        rootY = find(y)
        if rootX and rootY and rootX != rootY:
            parent[rootY] = rootX
    
    for piece in pieces_set:
        if piece > nx:
            union(piece, piece - nx)
        if piece < nx * (ny - 1):
            union(piece, piece + nx)
        if piece % nx != 1:
            union(piece, piece - 1)
        if piece % nx != 0:
            union(piece, piece + 1)
    
    groups = set(find(piece) for piece in pieces_set)
    
    return len(pieces) - len(groups)

print("1:")
pieces_groups = group_groups(pieces)
a = len(pieces) - len(pieces_groups)
print(a)
                    
print("2:")
pieces_groups = group_groups2(pieces)
b = pieces_groups
print(b)
