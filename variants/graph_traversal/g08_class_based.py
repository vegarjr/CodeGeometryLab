"""G08: Object-oriented — ShortestPathFinder class with method decomposition."""

import heapq


class ShortestPathFinder:
    def __init__(self, adj, source):
        self.adj = adj
        self.source = source
        self.dist = {node: float('inf') for node in adj}
        self.dist[source] = 0
        self._heap = [(0, source)]

    def _process_node(self, d, u):
        if d > self.dist[u]:
            return
        neighbors = self.adj[u]
        self._relax_edges(u, d, neighbors)

    def _relax_edges(self, u, d, neighbors):
        for v, w in neighbors:
            nd = d + w
            if nd < self.dist[v]:
                self.dist[v] = nd
                heapq.heappush(self._heap, (nd, v))

    def run(self):
        while self._heap:
            d, u = heapq.heappop(self._heap)
            self._process_node(d, u)
        return self.dist


def compute(adj, source):
    finder = ShortestPathFinder(adj, source)
    return finder.run()
