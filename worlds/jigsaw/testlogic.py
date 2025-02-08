nx = 5
ny = 5

pieces = [1, 9, 14]

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
    
print(len(pieces_groups), len(pieces) - len(pieces_groups))