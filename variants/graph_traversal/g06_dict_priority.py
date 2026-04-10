"""G06: Manual priority queue using a dict — scan for minimum each step."""


def compute(adj, source):
    dist = {node: float('inf') for node in adj}
    dist[source] = 0
    unvisited = set(adj.keys())

    while unvisited:
        # Find unvisited node with minimum distance
        u = None
        min_d = float('inf')
        for node in unvisited:
            if dist[node] < min_d:
                min_d = dist[node]
                u = node

        if u is None or min_d == float('inf'):
            break

        unvisited.remove(u)
        for v, w in adj[u]:
            nd = min_d + w
            if nd < dist[v]:
                dist[v] = nd

    return dist
