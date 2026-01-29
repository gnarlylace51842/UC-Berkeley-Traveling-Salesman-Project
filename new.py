import math
from itertools import combinations

def read_tsplib_file(filepath):
    coords = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        start = False
        for line in lines:
            line = line.strip()
            if line == "NODE_COORD_SECTION":
                start = True
                continue
            if line == "EOF":
                break
            if start:
                parts = line.split()
                if len(parts) >= 3:
                    _, x, y = parts
                    coords.append((float(x), float(y)))
    return coords

def tsplib_distance(a, b):
    return int(math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2) + 0.5)

def tsp_dynamic(nodes):
    n = len(nodes)
    dist = []

    for i in range(n):
        row = []
        for j in range(n):
            d = tsplib_distance(nodes[i], nodes[j])
            row.append(d)
        dist.append(row)
    
    dp = {}
    path = {}

    for k in range(1, n):
        dp[(1 << k, k)] = dist[0][k]
        path[(1 << k, k)] = 0

    for subset_size in range(2, n):
        for subset in combinations(range(1, n), subset_size):
            bits = sum(1 << bit for bit in subset)
            for k in subset:
                prev_bits = bits & ~(1 << k)
                min_dist = float('inf')
                prev_node = None
                for m in subset:
                    if m == k:
                        continue
                    if (prev_bits, m) in dp:
                        new_dist = dp[(prev_bits, m)] + dist[m][k]
                        if new_dist < min_dist:
                            min_dist = new_dist
                            prev_node = m
                dp[(bits, k)] = min_dist
                path[(bits, k)] = prev_node

    bits = (1 << n) - 2
    min_cost = float('inf')
    last_node = None
    for k in range(1, n):
        cost = dp[(bits, k)] + dist[k][0]
        if cost < min_cost:
            min_cost = cost
            last_node = k

    opt_path = [0]
    bitmask = bits
    curr_node = last_node
    for _ in range(n - 1):
        opt_path.append(curr_node)
        prev = path[(bitmask, curr_node)]
        bitmask &= ~(1 << curr_node)
        curr_node = prev
    opt_path.append(0)
    opt_path = list(reversed(opt_path))

    coords_path = [nodes[i] for i in opt_path]
    return min_cost, coords_path

filepath = "/Users/dylanashraf/Downloads/TSP Data/burma14.tsp"
nodes = read_tsplib_file(filepath)

min_cost, tour_path = tsp_dynamic(nodes)

print("TSPLIB-style optimal tour cost:", min_cost)
print("Tour path (in coordinates):", tour_path)