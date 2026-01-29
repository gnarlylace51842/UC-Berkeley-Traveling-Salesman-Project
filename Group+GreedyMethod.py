from itertools import permutations
import matplotlib.pyplot as plt
import time
import tsplib95
import math
import random

# Plan: Instead of bruteforcing 100 nodes, I would partition these 100 nodes into equal groups of 10. (DONE)
# Each group would be classified by how close they are to other nodes. (DONE)
# Then, in these groups of 10, I would find the smallest path using BruteForce in these groups of 10. (DONE)
# Lastly, I'll find a way to connect each group to one another in the smallest possible path.
# Then, by adding the path cost between each partition, and the path cost to get from one partition to another, I would find the path cost for the TSP. (DONE)



nodes = [
    (252, 898), (129, 417), (543, 692), (961, 736), (633, 325), (114, 583), (455, 390), (835, 612), (359, 102), (753, 768),
    (642, 421), (924, 882), (387, 243), (515, 961), (167, 342), (700, 141), (278, 548), (840, 280), (300, 888), (472, 770),
    (603, 201), (111, 741), (929, 544), (457, 322), (608, 659), (390, 576), (248, 462), (837, 449), (170, 274), (974, 230),
    (431, 650), (146, 931), (793, 913), (199, 704), (384, 384), (997, 317), (280, 303), (771, 520), (615, 354), (541, 488),
    (873, 132), (707, 876), (333, 319), (894, 345), (103, 185), (499, 420), (386, 736), (660, 928), (321, 911), (755, 392),
    (428, 289), (600, 782), (222, 669), (510, 326), (183, 570), (941, 110), (297, 153), (572, 432), (316, 604), (655, 301),
    (144, 625), (512, 589), (287, 360), (858, 756), (471, 150), (639, 975), (209, 845), (312, 459), (501, 212), (818, 837),
    (130, 785), (354, 987), (773, 660), (620, 134), (213, 356), (454, 868), (982, 752), (726, 202), (237, 518), (906, 392),
    (574, 619), (346, 222), (690, 701), (824, 113), (541, 288), (912, 661), (477, 612), (390, 509), (627, 575), (384, 846),
    (598, 242), (841, 508), (137, 307), (952, 977), (747, 449), (674, 356), (263, 781), (999, 550), (508, 185), (680, 902)
]

pathCostPerPartition = []

# Used to solve partitioned clusters
def euclidean(a, b):
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def solve_bruteForce(nodes):
    possiblePaths = []
    costAndIndex = []

    for p in permutations(nodes[1:]):  # skip the first node
        path = [nodes[0]] + list(p)  # full round-trip
        possiblePaths.append(path)

    for path in possiblePaths:
        total_cost = 0
        for i in range(len(path) - 1):
            total_cost += euclidean(path[i], path[i + 1])
        costAndIndex.append((total_cost, path))

    min_cost = float('inf')
    min_cost_path = None
    for cost, path in costAndIndex:
        if cost < min_cost:
            min_cost = cost
            min_cost_path = path
    
    print(min_cost_path)
    entry, exit = min_cost_path[0], min_cost_path[-1]
    
    return min_cost, entry, exit

def clusters(nodes, clusterSize):
    unvisited = nodes.copy()
    clusters=[]

    while len(unvisited) >= clusterSize:
        cluster = []
        start_node = random.choice(unvisited)
        cluster.append(start_node)
        unvisited.remove(start_node)

        while len(cluster) < clusterSize:
            last = cluster[-1]
            testNextNode = None
            testDistance = float("inf")

            for i in unvisited:
                if euclidean(last, i) < testDistance:
                    testNextNode = i
                    testDistance = euclidean(last, i)
            cluster.append(testNextNode)
            unvisited.remove(testNextNode)
        
        clusters.append(cluster)
    
    return clusters

def greedy_cluster_connection(pathCostPerPartition):
    n = len(pathCostPerPartition)
    visited = [False] * n
    total_cost = 0
    order = []

    current = 0
    visited[current] = True
    total_cost += pathCostPerPartition[current][0]
    order.append(current)

    while len(order) < n:
        current_exit = pathCostPerPartition[current][2]
        best_dist = float("inf")
        next_cluster = -1

        for i in range(n):
            if not visited[i]:
                candidate_entry = pathCostPerPartition[i][1]
                dist = euclidean(current_exit, candidate_entry)
                if dist < best_dist:
                    best_dist = dist
                    next_cluster = i

        total_cost += pathCostPerPartition[next_cluster][0]
        total_cost += euclidean(pathCostPerPartition[current][2], pathCostPerPartition[next_cluster][1])
        visited[next_cluster] = True
        order.append(next_cluster)
        current = next_cluster

    total_cost += euclidean(pathCostPerPartition[current][2], pathCostPerPartition[order[0]][1])

    print("Greedy cluster order:", order)
    return total_cost

def solve_grouped_tsp(nodes, clusterSize):
    Clusters = clusters(nodes, clusterSize)
    pathCostPerPartition = []

    for cluster in Clusters:
        result = solve_bruteForce(cluster)
        pathCostPerPartition.append(result)

    total_cost = greedy_cluster_connection(pathCostPerPartition)
    print(f"\nTotal estimated TSP cost (greedy between clusters): {total_cost:.2f}")

solve_grouped_tsp(nodes, 10)