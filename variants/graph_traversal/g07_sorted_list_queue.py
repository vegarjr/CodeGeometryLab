"""G07: Sorted list as priority queue — re-sorts after each insertion."""


def compute(adj, source):
    dist = {node: float('inf') for node in adj}
    dist[source] = 0
    queue = [(0, source)]

    while queue:
        d, u = queue.pop(0)  # take smallest (front of sorted list)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                queue.append((nd, v))
                queue.sort()  # re-sort after each insert

    return dist
