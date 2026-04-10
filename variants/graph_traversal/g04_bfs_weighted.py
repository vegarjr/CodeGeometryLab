"""G04: BFS-style with deque — re-queues nodes when distance improves (SPFA-like)."""

from collections import deque


def compute(adj, source):
    dist = {node: float('inf') for node in adj}
    dist[source] = 0
    queue = deque([source])
    in_queue = {source}

    while queue:
        u = queue.popleft()
        in_queue.discard(u)
        for v, w in adj[u]:
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd
                if v not in in_queue:
                    queue.append(v)
                    in_queue.add(v)

    return dist
