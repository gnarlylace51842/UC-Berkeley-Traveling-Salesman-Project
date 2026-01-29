from itertools import combinations
import matplotlib.pyplot as plt
import time
import math



# all nodes
nodes_lists = [
    [(415, 123)],
    [(71, 82), (558, 918)],
    [(108, 959), (524, 72), (78, 580)],
    [(457, 505), (176, 357), (576, 672), (662, 965)],
    [(928, 595), (917, 162), (232, 233), (667, 702), (49, 38)],
    [(703, 231), (301, 956), (971, 261), (201, 767), (989, 645), (847, 554)],
    [(348, 44), (65, 597), (750, 633), (79, 694), (164, 628), (496, 324), (918, 903)],
    [(952, 574), (966, 182), (364, 150), (396, 56), (778, 155), (238, 180), (184, 506), (482, 829)],
    [(576, 313), (958, 757), (190, 125), (676, 160), (935, 481), (545, 832), (113, 680), (815, 865), (390, 372)],
    [(203, 932), (963, 81), (268, 506), (785, 91), (658, 96), (376, 422), (37, 561), (73, 131), (298, 148), (659, 754)],
    [(418, 153), (885, 67), (376, 427), (174, 567), (197, 444), (18, 858), (201, 48), (235, 252), (936, 339), (605, 38), (883, 981)],
    [(193, 594), (137, 960), (563, 393), (443, 698), (690, 761), (410, 468), (556, 930), (885, 696), (569, 389), (811, 648), (367, 888), (532, 344)],
    [(62, 277), (986, 712), (203, 915), (281, 568), (359, 335), (502, 239), (330, 819), (374, 310), (29, 605), (480, 757), (862, 678), (355, 255), (246, 274)],
    [(482, 313), (931, 572), (459, 699), (992, 742), (312, 783), (624, 52), (519, 462), (417, 137), (83, 48), (652, 369), (450, 559), (222, 372), (903, 981), (851, 241)],
    [(673, 399), (294, 618), (333, 408), (470, 3), (122, 532), (197, 948), (484, 254), (324, 399), (903, 873), (226, 790), (466, 291), (440, 540), (594, 205), (160, 898), (404, 876)],
    [(405, 923), (45, 72), (1000, 494), (321, 428), (182, 828), (812, 10), (598, 441), (988, 718), (991, 882), (610, 373), (526, 528), (80, 60), (142, 317), (317, 331), (231, 453), (866, 12)],
    [(291, 66), (520, 376), (793, 155), (285, 525), (876, 605), (447, 614), (56, 715), (52, 331), (424, 136), (664, 183), (390, 82), (863, 88), (71, 246), (48, 564), (874, 629), (636, 996), (521, 485)],
    [(123, 739), (218, 533), (503, 623), (962, 212), (821, 616), (101, 247), (577, 171), (59, 343), (347, 19), (340, 406), (974, 841), (474, 569), (655, 494), (947, 433), (33, 292), (409, 313), (550, 572), (313, 225)],
    [(886, 327), (842, 354), (255, 205), (915, 736), (61, 213), (301, 110), (530, 128), (639, 311), (498, 315), (887, 876), (636, 184), (464, 59), (948, 294), (136, 976), (377, 293), (14, 907), (991, 969), (791, 329), (487, 692)],
    [(105, 288), (757, 581), (683, 716), (469, 662), (987, 851), (517, 989), (364, 860), (430, 713), (221, 694), (291, 68), (723, 682), (211, 488), (333, 860), (27, 282), (18, 134), (346, 549), (430, 27), (91, 343), (163, 193), (961, 172)],
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

runtimes = []
for nodes in nodes_lists:
    start = time.time()
    if len(nodes) <= 20:
        tsp_dp(nodes)
        end = time.time()
        runtimes.append(end - start)
    else:
        runtimes.append(None)

x_vals, y_vals = [], []
i = 0
while i < len(runtimes):
    t = runtimes[i]
    if t is not None:
        x_vals.append(i + 1)
    i += 1
i = 0
while i < len(runtimes):
    t = runtimes[i]
    if t is not None:
        y_vals.append(t)
    i += 1

plt.figure(figsize=(10, 6))
plt.plot(x_vals, y_vals, marker='o')
plt.xlabel("Number of Nodes")
plt.ylabel("Runtime (seconds)")
plt.title("Runtime of TSP DP vs Number of Nodes")
plt.grid(True)
plt.tight_layout()
plt.show()