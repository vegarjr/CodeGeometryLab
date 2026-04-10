"""G09: Iterative improvement — repeatedly scans all edges until no change."""


def compute(adj, source):
    dist = {node: float('inf') for node in adj}
    dist[source] = 0

    changed = True
    while changed:
        changed = False
        for u in adj:
            if dist[u] == float('inf'):
                continue
            for v, w in adj[u]:
                nd = dist[u] + w
                if nd < dist[v]:
                    dist[v] = nd
                    changed = True

    return dist
