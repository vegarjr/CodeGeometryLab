"""Graph traversal task definition: reference graph, correctness gate, variant loading."""

import importlib
import random


def generate_reference_graph(n_nodes=200, n_edges=800, seed=42):
    """Generate a deterministic weighted directed graph as adjacency list.

    Returns dict: {node_id: [(neighbor_id, weight), ...]}
    """
    rng = random.Random(seed)
    adj = {i: [] for i in range(n_nodes)}
    # Ensure connectivity: chain 0→1→2→...→n-1
    for i in range(n_nodes - 1):
        w = rng.randint(1, 20)
        adj[i].append((i + 1, w))
    # Add random edges
    edges_added = n_nodes - 1
    while edges_added < n_edges:
        u = rng.randint(0, n_nodes - 1)
        v = rng.randint(0, n_nodes - 1)
        if u != v:
            w = rng.randint(1, 20)
            adj[u].append((v, w))
            edges_added += 1
    return adj


REFERENCE_GRAPH = generate_reference_graph()
REFERENCE_SOURCE = 0
REFERENCE_PARAMS = dict(adj=REFERENCE_GRAPH, source=REFERENCE_SOURCE)

# Scaling graphs
SCALING_CONFIGS = [
    {"n_nodes": 100, "n_edges": 400},
    {"n_nodes": 200, "n_edges": 800},
    {"n_nodes": 500, "n_edges": 2000},
    {"n_nodes": 1000, "n_edges": 4000},
]

VARIANT_MODULES = [
    "variants.graph_traversal.g01_dijkstra_heap",
    "variants.graph_traversal.g02_dijkstra_no_skip",
    "variants.graph_traversal.g03_bellman_ford",
    "variants.graph_traversal.g04_bfs_weighted",
    "variants.graph_traversal.g05_recursive_relax",
    "variants.graph_traversal.g06_dict_priority",
    "variants.graph_traversal.g07_sorted_list_queue",
    "variants.graph_traversal.g08_class_based",
    "variants.graph_traversal.g09_iterative_improve",
    "variants.graph_traversal.g10_bidirectional",
]

VARIANT_NAMES = [m.rsplit(".", 1)[1] for m in VARIANT_MODULES]


def load_variants():
    variants = []
    for name, module_path in zip(VARIANT_NAMES, VARIANT_MODULES):
        mod = importlib.import_module(module_path)
        variants.append((name, mod.compute))
    return variants


def compute_reference():
    mod = importlib.import_module(VARIANT_MODULES[0])
    return mod.compute(**REFERENCE_PARAMS)


def correctness_gate(verbose=True):
    """Verify all variants produce correct shortest-path distances.

    Tolerance: exact match on reachable nodes (all weights are integers,
    so shortest paths are exact).
    """
    reference = compute_reference()
    variants = load_variants()
    report = {}

    for name, compute_fn in variants:
        try:
            result = compute_fn(**REFERENCE_PARAMS)
            # Compare distances for all nodes
            match = True
            mismatches = 0
            for node in reference:
                ref_d = reference[node]
                res_d = result.get(node, float('inf'))
                if abs(ref_d - res_d) > 1e-9:
                    match = False
                    mismatches += 1

            report[name] = {"passed": match, "result": result}
            if verbose:
                status = "PASS" if match else "FAIL"
                if not match:
                    print(f"  {name}: {status} ({mismatches} nodes differ)")
                else:
                    print(f"  {name}: {status}")
        except Exception as e:
            report[name] = {"passed": False, "result": None, "error": str(e)}
            if verbose:
                print(f"  {name}: ERROR — {e}")

    passed = [n for n, r in report.items() if r["passed"]]
    failed = [n for n, r in report.items() if not r["passed"]]

    if verbose:
        print(f"\n{len(passed)}/{len(report)} variants passed correctness gate.")
        if failed:
            print(f"Failed: {failed}")

    return report


if __name__ == "__main__":
    print("Running graph traversal correctness gate...")
    correctness_gate()
