"""Unified geometric metrics: collects graph, trajectory, and fractal metrics."""

from representations.trace_graph import (
    build_call_graph,
    build_temporal_graph,
    build_line_flow_graph,
    graph_metrics,
)
from representations.state_trajectory import build_trajectory, trajectory_metrics
from representations.fractal_summary import fractal_metrics


def compute_all_geometric_metrics(trace_record, trajectory_points=100):
    """Compute all geometric metrics for one trace record.

    Returns a flat dict of metric_name → float.
    """
    all_metrics = {}

    # --- Graph metrics ---
    call_graph = build_call_graph(trace_record)
    cg_metrics = graph_metrics(call_graph)
    for k, v in cg_metrics.items():
        all_metrics[f"cg_{k}"] = v

    temporal_graph = build_temporal_graph(trace_record)
    tg_metrics = graph_metrics(temporal_graph)
    for k, v in tg_metrics.items():
        all_metrics[f"tg_{k}"] = v

    line_graph = build_line_flow_graph(trace_record)
    lg_metrics = graph_metrics(line_graph)
    for k, v in lg_metrics.items():
        all_metrics[f"lg_{k}"] = v

    # --- Trajectory metrics ---
    trajectory = build_trajectory(trace_record, n_points=trajectory_points)
    traj_metrics = trajectory_metrics(trajectory)
    for k, v in traj_metrics.items():
        all_metrics[f"traj_{k}"] = v

    # --- Fractal metrics ---
    frac_metrics = fractal_metrics(trace_record)
    for k, v in frac_metrics.items():
        all_metrics[f"frac_{k}"] = v

    return all_metrics
