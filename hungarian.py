#! /usr/bin/env python3

# Below is a pure-Python (no dependencies) implementation of the Assignment Problem using the Hungarian (Kuhn–Munkres) algorithm.
# It solves the minimum-cost perfect matching on a bipartite graph represented as a cost matrix.
# Works for rectangular matrices (pads internally)
# Time complexity: O(n³)
def hungarian(cost):
    """
    Solve the assignment problem using the Hungarian algorithm.

    Args:
        cost: 2D list (n x m) where cost[i][j] is the cost of assigning
              worker i to job j.

    Returns:
        assignment: list of (row, col) assignments
        total_cost: sum of assigned costs
    """

    n = len(cost)
    m = len(cost[0])

    # Hungarian requires n <= m; transpose if needed
    transposed = False
    if n > m:
        cost = list(map(list, zip(*cost)))
        n, m = m, n
        transposed = True

    INF = float("inf")

    u = [0] * (n + 1)  # row potentials
    v = [0] * (m + 1)  # column potentials
    p = [0] * (m + 1)  # matching for columns
    way = [0] * (m + 1)

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (m + 1)
        used = [False] * (m + 1)

        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = 0

            for j in range(1, m + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j

            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta

            j0 = j1
            if p[j0] == 0:
                break

        # Augmenting
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    # Build assignment
    assignment = []
    total_cost = 0
    for j in range(1, m + 1):
        if p[j] != 0:
            i = p[j] - 1
            j_idx = j - 1
            if transposed:
                assignment.append((j_idx, i))
                total_cost += cost[i][j_idx]
            else:
                assignment.append((i, j_idx))
                total_cost += cost[i][j_idx]

    return assignment, total_cost
