"""Representation A: Execution graph from trace events.

Nodes represent functions/blocks. Edges represent call relationships
and temporal transitions.
"""

import networkx as nx
from collections import Counter


def build_call_graph(trace_record):
    """Build a directed call graph from trace events.

    Nodes: unique functions. Edges: caller→callee with call count as weight.
    """
    G = nx.DiGraph()
    call_edges = Counter()

    for event in trace_record.events:
        if event.event_type == "call":
            G.add_node(event.function_name)
            if event.parent_function:
                call_edges[(event.parent_function, event.function_name)] += 1

    for (caller, callee), count in call_edges.items():
        G.add_edge(caller, callee, weight=count)

    return G


def build_temporal_graph(trace_record, sample_rate=1):
    """Build a temporal transition graph from call/return events.

    Nodes: (function_name, depth) pairs. Edges: temporal succession
    between consecutive events, weighted by transition count.
    """
    G = nx.DiGraph()
    transitions = Counter()

    call_return_events = [
        e for e in trace_record.events
        if e.event_type in ("call", "return")
    ]

    # Sample to keep graph manageable
    if sample_rate > 1:
        call_return_events = call_return_events[::sample_rate]

    prev_node = None
    for event in call_return_events:
        node = f"{event.function_name}@d{event.depth}"
        G.add_node(node, function=event.function_name, depth=event.depth)
        if prev_node is not None and prev_node != node:
            transitions[(prev_node, node)] += 1
        prev_node = node

    for (src, dst), count in transitions.items():
        G.add_edge(src, dst, weight=count)

    return G


def build_line_flow_graph(trace_record, max_nodes=500):
    """Build a line-level flow graph from line events.

    Nodes: (function_name, lineno). Edges: successive line transitions.
    Sampled to max_nodes to keep manageable.
    """
    G = nx.DiGraph()
    transitions = Counter()

    line_events = [e for e in trace_record.events if e.event_type == "line"]

    # Sample if too many
    step = max(1, len(line_events) // max_nodes)
    sampled = line_events[::step]

    prev_node = None
    for event in sampled:
        node = f"{event.function_name}:{event.lineno}"
        G.add_node(node, function=event.function_name, lineno=event.lineno)
        if prev_node is not None:
            transitions[(prev_node, node)] += 1
        prev_node = node

    for (src, dst), count in transitions.items():
        G.add_edge(src, dst, weight=count)

    return G


def graph_metrics(G):
    """Compute structural metrics for a directed graph."""
    metrics = {}

    metrics["node_count"] = G.number_of_nodes()
    metrics["edge_count"] = G.number_of_edges()

    if G.number_of_nodes() == 0:
        return metrics

    # Degree statistics
    in_degrees = [d for _, d in G.in_degree()]
    out_degrees = [d for _, d in G.out_degree()]
    metrics["max_in_degree"] = max(in_degrees) if in_degrees else 0
    metrics["max_out_degree"] = max(out_degrees) if out_degrees else 0
    metrics["mean_out_degree"] = sum(out_degrees) / len(out_degrees) if out_degrees else 0

    # Density
    metrics["density"] = nx.density(G)

    # Weakly connected components
    if G.number_of_nodes() > 0:
        wcc = list(nx.weakly_connected_components(G))
        metrics["n_weakly_connected_components"] = len(wcc)
        metrics["largest_wcc_size"] = max(len(c) for c in wcc)

    # DAG properties
    metrics["is_dag"] = nx.is_directed_acyclic_graph(G)
    if metrics["is_dag"] and G.number_of_nodes() > 0:
        metrics["dag_longest_path"] = len(nx.dag_longest_path(G))
    else:
        metrics["dag_longest_path"] = 0

    # Self-loops
    metrics["self_loop_count"] = nx.number_of_selfloops(G)

    # Strongly connected components (cycles)
    scc = list(nx.strongly_connected_components(G))
    metrics["n_strongly_connected_components"] = len(scc)
    metrics["largest_scc_size"] = max(len(c) for c in scc) if scc else 0

    return metrics
