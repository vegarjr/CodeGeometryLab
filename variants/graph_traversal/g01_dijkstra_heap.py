"""G01: Classic Dijkstra with heapq — canonical textbook implementation."""

import heapq


def compute(adj, source):
    dist = {node: float('inf') for node in adj}
    dist[source] = 0
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))

    return dist
