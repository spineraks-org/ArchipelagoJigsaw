import random


nx = 5
ny = 5

# random.seed(1)
pieces = random.sample(range(1, nx * ny + 1), 5)

pieces_set = set(pieces)
countx = sum(1 for i in pieces if (i + 1) in pieces_set and i % nx != 0)
county = sum(1 for i in pieces if (i + nx) in pieces_set)

print(pieces)
print(countx+county)