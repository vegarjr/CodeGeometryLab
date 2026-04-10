"""G02: Dijkstra without the stale-entry skip — processes all heap entries."""

import heapq


def compute(adj, source):
    dist = {node: float('inf') for node in adj}
    dist[source] = 0
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        # No skip: always process, even if stale
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))

    return dist
