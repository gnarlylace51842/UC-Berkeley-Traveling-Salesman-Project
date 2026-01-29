# Note: Does not work with nodes less than 6, because of the nature of 3-opt. 
# Without a minimum of 6 nodes, it cannot make 3 non-empty segments, since each segment has to have a minimum of length 2.

nodes = [
    (252, 898), (129, 417), (543, 692), (961, 736), (633, 325), (114, 583), (455, 390), (835, 612), (359, 102), (753, 768)
]

def euclidean(a, b):
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def build_dist_matrix(nodes):
    n = len(nodes)
    dist = []
    for i in range(n):
        row = []
        for j in range(n):
            d = euclidean(nodes[i], nodes[j])
            row.append(d)
        dist.append(row)
    return dist

def tour_length(tour, dist):
    n = len(tour)
    s = 0
    for i in range(n):
        s += dist[tour[i]][tour[(i+1) % n]]
    return s

# start with greedy tour to converge to fastest tour asap
def greedy_tour(dist):
    n = len(dist)
    start = 0
    unvisited = []
    for i in range(n):
        unvisited.append(i)
    tour = [start]
    unvisited.remove(start)
    current = start
    while unvisited:
        nxt = min(unvisited, key=lambda j: dist[current][j])
        tour.append(nxt)
        unvisited.remove(nxt)
        current = nxt
    print(tour)
    return tour

def three_opt(tour, D):
    n = len(tour)
    def dist(a, b): return D[a][b]
    max_passes=None

    improved = True
    passes = 0
    while improved and (max_passes is None or passes < max_passes):
        improved = False
        passes += 1

        for i in range(n):
            a = tour[i]
            b = tour[(i+1) % n]  # start of B
            for j in range(i+1, i + n - 3):
                j_remainder = j % n
                c = tour[j_remainder]
                d = tour[(j_remainder+1) % n]  # start of C
                # ensure segments don't wrap over each other weirdly
                if (j_remainder == (i+1) % n):  # B would be empty
                    continue
                for k in range(j+1, i + n - 1):
                    k_remainder = k % n
                    e = tour[k_remainder]
                    f = tour[(k_remainder+1) % n]  # start of D
                    if (k_remainder == (j_remainder+1) % n):  # C would be empty
                        continue

                    # old boundary edges removed:
                    old = dist(a, b) + dist(c, d) + dist(e, f)

                    # extractx the actual B and C segments as sequences of node indices
                    # B = tour[i+1 .. j], C = tour[j+1 .. k]
                    def slice_path(start_idx, end_idx):
                        res = []
                        x = start_idx % n
                        while True:
                            res.append(tour[x])
                            if x == end_idx % n:
                                break
                            x = (x + 1) % n
                        return res

                    B = slice_path(i+1, j_remainder)
                    C = slice_path(j_remainder+1, k_remainder)

                    # iterates through the 8 reconnection patterns of B/C: order (B,C) vs (C,B), and reverse flags
                    candidates = []
                    for first_seg_name, first_seg in (('B', B), ('C', C)):
                        second_seg_name, second_seg = ('C', C) if first_seg_name == 'B' else ('B', B)
                        for rev1 in (False, True):
                            for rev2 in (False, True):
                                # computes new boundary distances only:
                                x = first_seg[::-1] if rev1 else first_seg
                                y = second_seg[::-1] if rev2 else second_seg

                                # ignores the no-op case where order and orientations are unchanged
                                if first_seg_name == 'B' and not rev1 and not rev2 and second_seg_name == 'C':
                                    continue

                                new_bound = dist(a, x[0]) + dist(x[-1], y[0]) + dist(y[-1], f)
                                gain = old - new_bound
                                if gain > (1 * 10**-12):
                                    candidates.append((gain, first_seg_name, rev1, rev2))

                    if not candidates:
                        continue

                    # picks the best reconnection
                    candidates.sort(reverse=True, key=lambda z: z[0])
                    placeholder, first_seg_name, rev1, rev2 = candidates[0]

                    # applies the best move: rebuild the tour as A + X + Y + D
                    X = (B[::-1] if rev1 else B) if first_seg_name == 'B' else (C[::-1] if rev1 else C)
                    Y = (C[::-1] if rev2 else C) if first_seg_name == 'B' else (B[::-1] if rev2 else B)

                    # A = tour[0..i], D = tour[k+1..end] + tour[0..i] wraps naturally ONLY if we reconstruct linearly
                    A = slice_path(0, i)
                    Dseg = slice_path((k_remainder+1) % n, (i) % n)  # from f to a, inclusive. 

                    # merges A + X + Y + D properly
                    new_tour = A + X + Y + Dseg[:-1]

                    tour = new_tour
                    improved = True
                    # restart outer loops to respect the new structure
                    break
                if improved:
                    break
            if improved:
                break
    return tour

def solve_tsp_3opt(nodes):
    dist = build_dist_matrix(nodes)
    tour = greedy_tour(dist)
    tour = three_opt(tour, dist)
    return tour, tour_length(tour, dist)



tour, length = solve_tsp_3opt(nodes)
print("Tour length:", length)
print("Tour (indices):", tour)
# city coordinates:
# ordered_coords = [nodes[i] for i in tour]
# print("City Coordinates:", ordered_coords)