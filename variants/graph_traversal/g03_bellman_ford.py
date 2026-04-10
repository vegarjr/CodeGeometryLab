"""G03: Bellman-Ford — relaxes all edges V-1 times."""


def compute(adj, source):
    dist = {node: float('inf') for node in adj}
    dist[source] = 0

    nodes = list(adj.keys())
    n = len(nodes)

    for _ in range(n - 1):
        updated = False
        for u in nodes:
            if dist[u] == float('inf'):
                continue
            for v, w in adj[u]:
                nd = dist[u] + w
                if nd < dist[v]:
                    dist[v] = nd
                    updated = True
        if not updated:
            break

    return dist
