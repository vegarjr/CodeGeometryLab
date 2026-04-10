"""G05: Recursive relaxation — recursively relaxes neighbors when improvement found."""

import sys

_ORIGINAL_LIMIT = sys.getrecursionlimit()


def _relax(adj, dist, u):
    for v, w in adj[u]:
        nd = dist[u] + w
        if nd < dist[v]:
            dist[v] = nd
            _relax(adj, dist, v)


def compute(adj, source):
    sys.setrecursionlimit(max(len(adj) * 10 + 100, _ORIGINAL_LIMIT))
    try:
        dist = {node: float('inf') for node in adj}
        dist[source] = 0
        _relax(adj, dist, source)
        return dist
    finally:
        sys.setrecursionlimit(_ORIGINAL_LIMIT)
