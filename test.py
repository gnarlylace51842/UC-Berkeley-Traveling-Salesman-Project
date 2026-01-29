import tsplib95
import math
import random

filepath = "/Users/dylanashraf/Downloads/TSP Data/burma14.tsp"

# Load the TSP problem using tsplib95
problem = tsplib95.load(filepath)

# Extract node coordinates
coords = {node: problem.node_coords[node] for node in problem.get_nodes()}

# Proper TSPLIB distance calculation
def tsp_distance(a, b):
    return problem.get_weight(a, b)  # Uses correct EDGE_WEIGHT_TYPE rules

def total_path_distance(path):
    return sum(tsp_distance(path[i], path[i+1]) for i in range(len(path) - 1))

def solve_unravel(nodes):
    start = nodes[0]
    unvisited = nodes[1:]
    path = [start]
    current = start

    while unvisited:
        next_node = min(unvisited, key=lambda x: tsp_distance(current, x))
        path.append(next_node)
        unvisited.remove(next_node)
        current = next_node

    improved = True
    while improved:
        improved = False
        for i in range(1, len(path) - 2):
            for j in range(i + 1, len(path)):
                if j - i == 1:
                    continue
                new_path = path[:i] + path[i:j][::-1] + path[j:]
                if total_path_distance(new_path) < total_path_distance(path):
                    path = new_path
                    improved = True

    return total_path_distance(path), path[0], path[-1]

def clusters(nodes, clusterSize):
    unvisited = nodes.copy()
    clusters_list = []

    while len(unvisited) >= clusterSize:
        cluster = []
        start_node = random.choice(unvisited)
        cluster.append(start_node)
        unvisited.remove(start_node)

        while len(cluster) < clusterSize:
            last = cluster[-1]
            next_node = min(unvisited, key=lambda x: tsp_distance(last, x))
            cluster.append(next_node)
            unvisited.remove(next_node)

        clusters_list.append(cluster)

    return clusters_list

def cluster_connection(clusters):
    connections = {}
    for i in range(len(clusters)):
        for j in range(len(clusters)):
            if i == j:
                continue
            min_cost = float('inf')
            min_pair = (None, None)
            for node_a in clusters[i]:
                for node_b in clusters[j]:
                    dist = tsp_distance(node_a, node_b)
                    if dist < min_cost:
                        min_cost = dist
                        min_pair = (node_a, node_b)
            connections[(i, j)] = {"cost": min_cost, "from": min_pair[0], "to": min_pair[1]}
    return connections

def inter_cluster_cost(order, pathCostPerPartition, cluster_connections):
    cost = 0
    for i in order:
        cost += pathCostPerPartition[i][0]
    for i in range(len(order) - 1):
        cost += cluster_connections[(order[i], order[i+1])]["cost"]
    return cost

def calculate_totalCost(pathCostPerPartition, cluster_connections):
    num_clusters = len(pathCostPerPartition)
    order = list(range(num_clusters))
    best_order = order[:]
    min_total_cost = inter_cluster_cost(best_order, pathCostPerPartition, cluster_connections)

    improved = True
    while improved:
        improved = False
        for i in range(1, num_clusters - 2):
            for j in range(i + 1, num_clusters):
                if j - i == 1:
                    continue
                new_order = best_order[:i] + best_order[i:j][::-1] + best_order[j:]
                new_cost = inter_cluster_cost(new_order, pathCostPerPartition, cluster_connections)
                if new_cost < min_total_cost:
                    best_order = new_order
                    min_total_cost = new_cost
                    improved = True

    print("Best cluster order:", best_order)
    return min_total_cost

# Run the solver
all_nodes = list(coords.keys())
clusters_list = clusters(all_nodes, 2)
pathCostPerPartition = [solve_unravel(cluster) for cluster in clusters_list]
cluster_connections = cluster_connection(clusters_list)

print("Cluster connections:", cluster_connections)
print("Estimated TSP cost:", calculate_totalCost(pathCostPerPartition, cluster_connections))