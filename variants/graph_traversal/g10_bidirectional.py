"""G10: Bidirectional-style — runs Dijkstra but processes nodes in two passes
(forward from source, then backward refinement)."""

import heapq


def compute(adj, source):
    # Forward pass
    dist = {node: float('inf') for node in adj}
    dist[source] = 0
    heap = [(0, source)]
    visited = set()

    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))

    # Backward refinement pass — check all edges for missed improvements
    for u in adj:
        if dist[u] == float('inf'):
            continue
        for v, w in adj[u]:
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd

    return dist
