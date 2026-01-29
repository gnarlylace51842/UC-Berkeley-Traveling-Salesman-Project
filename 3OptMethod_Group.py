from itertools import permutations
import math
import random

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


def euclidean(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def build_dist_lookup(points):
    dist = {p: {} for p in points}
    for i, a in enumerate(points):
        for j, b in enumerate(points):
            if i == j:
                dist[a][b] = 0.0
            elif b not in dist[a]:
                d = euclidean(a, b)
                dist[a][b] = d
                dist[b][a] = d
    return dist

def total_path_distance_fast(path, dist):
    return sum(dist[path[i]][path[i+1]] for i in range(len(path)-1))

def three_opt_open(path, dist):
    n = len(path)
    if n < 6:
        return path

    improved = True
    current_len = total_path_distance_fast(path, dist)

    while improved:
        improved = False
        # i starts at 1 to avoid constantly touching the head segment
        for i in range(1, n - 4):
            for j in range(i + 1, n - 2):
                for k in range(j + 1, n):
                    A = path[:i]
                    B = path[i:j]
                    C = path[j:k]
                    D = path[k:]

                    # 7 other possible paths
                    candidates = [
                        A + B[::-1] + C      + D,
                        A + B      + C[::-1] + D,
                        A + B[::-1] + C[::-1] + D,
                        A + C      + B      + D,
                        A + C[::-1] + B      + D,
                        A + C      + B[::-1] + D,
                        A + C[::-1] + B[::-1] + D,
                    ]

                    best_local = None
                    best_len = current_len
                    for cand in candidates:
                        cand_len = total_path_distance_fast(cand, dist)
                        if cand_len + 1e-12 < best_len:
                            best_len = cand_len
                            best_local = cand

                    if best_local is not None:
                        path = best_local
                        current_len = best_len
                        n = len(path)
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break

    return path

def nn_seed_open(points):
    start = points[0]
    unvisited = points[1:]
    path = [start]
    cur = start
    while unvisited:
        nxt = min(unvisited, key=lambda x: euclidean(cur, x))
        path.append(nxt)
        unvisited.remove(nxt)
        cur = nxt
    return path

def make_clusters(points, cluster_size, seed=42):
    rng = random.Random(seed)
    unvisited = points[:]
    clusters = []

    while len(unvisited) >= cluster_size:
        cluster = []
        start_node = rng.choice(unvisited)
        cluster.append(start_node)
        unvisited.remove(start_node)

        while len(cluster) < cluster_size:
            last = cluster[-1]
            # pick nearest unvisited to last
            next_node, best_d = None, float("inf")
            for p in unvisited:
                d = euclidean(last, p)
                if d < best_d:
                    next_node, best_d = p, d
            cluster.append(next_node)
            unvisited.remove(next_node)

        clusters.append(cluster)

    if unvisited:
        clusters.append(unvisited[:])

    return clusters

def solve_cluster_three_opt(cluster_points):
    path = nn_seed_open(cluster_points)
    dist = build_dist_lookup(path)
    path = three_opt_open(path, dist)
    cost = total_path_distance_fast(path, build_dist_lookup(path))
    return cost, path[0], path[-1], path

def build_cluster_connections(cluster_list):
    connections = {}
    for i, A in enumerate(cluster_list):
        for j, B in enumerate(cluster_list):
            if i == j:
                continue
            min_cost = float("inf")
            min_pair = (None, None)
            for a in A:
                for b in B:
                    d = euclidean(a, b)
                    if d < min_cost:
                        min_cost = d
                        min_pair = (a, b)
            connections[(i, j)] = {"cost": min_cost, "from": min_pair[0], "to": min_pair[1]}
    return connections

def inter_cluster_cost(order, per_cluster_solutions, cluster_connections):
    total = 0.0
    for idx in order:
        total += per_cluster_solutions[idx][0]  # intra-cluster cost

    for a, b in zip(order, order[1:]):
        total += cluster_connections[(a, b)]["cost"]

    return total

def three_opt_order(order, cost_fn):
    n = len(order)
    if n < 6:
        return order

    best = order[:]
    best_cost = cost_fn(best)
    improved = True

    while improved:
        improved = False
        for i in range(1, n - 4):
            for j in range(i + 1, n - 2):
                for k in range(j + 1, n):
                    A = best[:i]
                    B = best[i:j]
                    C = best[j:k]
                    D = best[k:]

                    candidates = [
                        A + B[::-1] + C      + D,
                        A + B      + C[::-1] + D,
                        A + B[::-1] + C[::-1] + D,
                        A + C      + B      + D,
                        A + C[::-1] + B      + D,
                        A + C      + B[::-1] + D,
                        A + C[::-1] + B[::-1] + D,
                    ]
                    for cand in candidates:
                        c = cost_fn(cand)
                        if c + 1e-12 < best_cost:
                            best, best_cost = cand, c
                            improved = True
                            break
                if improved:
                    break
            if improved:
                break
    return best

def solve_tsp_clustered_three_opt(points, cluster_size=10, seed=42, optimize_cluster_order=True):
    cluster_list = make_clusters(points, cluster_size, seed=seed)

    per_cluster_solutions = []
    for cl in cluster_list:
        per_cluster_solutions.append(solve_cluster_three_opt(cl))

    cluster_connections = build_cluster_connections(cluster_list)

    base_order = list(range(len(cluster_list)))

    def order_cost(ordr):
        return inter_cluster_cost(ordr, per_cluster_solutions, cluster_connections)

    if optimize_cluster_order and len(base_order) >= 6:
        best_order = three_opt_order(base_order, order_cost)
    else:
        best_order = base_order

    total_cost = order_cost(best_order)
    return {
        "clusters": cluster_list,
        "per_cluster_solutions": per_cluster_solutions,
        "cluster_connections": cluster_connections,
        "cluster_order": best_order,
        "total_cost": total_cost
    }


if __name__ == "__main__":
    random.seed(0)
    res = solve_tsp_clustered_three_opt(nodes, cluster_size=10, seed=0, optimize_cluster_order=True)

    print("Cluster order:", res["cluster_order"])
    print("Total cost (intra + inter):", res["total_cost"])
    for idx in res["cluster_order"]:
        cost, start, end, path = res["per_cluster_solutions"][idx]
        print(f"Cluster {idx}: cost={cost:.3f}, start={start}, end={end}, size={len(path)}")