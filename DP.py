from itertools import combinations
import matplotlib.pyplot as plt
import time
import math

nodes = [
    (252, 898), (129, 417), (543, 692), (961, 736), (633, 325), (114, 583), (455, 390), (835, 612), (359, 102), (753, 768),
    (642, 421), (924, 882)
]

def euclidean(a, b):
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def tsp_dp(nodes):
    n = len(nodes)
    dist = []

    for i in range(n):
        row = []
        for j in range(n):
            d = euclidean(nodes[i], nodes[j])
            row.append(d)
        dist.append(row)
    
    dp = {}
    path = {}
    
    for k in range(1, n):
        visited = frozenset([0, k])
        dp[(visited, k)] = dist[0][k]
        path[(visited, k)] = 0

    # subsets > 1
    for subset_size in range(3, n + 1):
        for subset in combinations(range(n), subset_size):
            if 0 not in subset:
                continue 
            visited = frozenset(subset)
            for k in subset:
                if k == 0:
                    continue
                min_cost = float('inf')
                prev_node = None
                prev_visited = visited - {k}
                for m in prev_visited:
                    if m == k:
                        continue
                    if (prev_visited, m) in dp:
                        cost = dp[(prev_visited, m)] + dist[m][k]
                        if cost < min_cost:
                            min_cost = cost
                            prev_node = m
                dp[(visited, k)] = min_cost
                path[(visited, k)] = prev_node

    all_nodes = frozenset(range(n))
    min_cost = float('inf')
    last_node = None
    for k in range(1, n):
        cost = dp[(all_nodes, k)] + dist[k][0]
        if cost < min_cost:
            min_cost = cost
            last_node = k

    # remake path
    current_node = last_node
    visited = set(range(n))
    order = [0]  # start from node 0
    while len(order) < n:
        order.append(current_node)
        visited_set = frozenset(visited)
        prev = path[(visited_set, current_node)]
        visited.remove(current_node)
        current_node = prev
    order.append(0)  # return to start

    coords_path = [nodes[i] for i in order]

    return min_cost, coords_path

print(tsp_dp(nodes))