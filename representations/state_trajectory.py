"""Representation B: State trajectory — execution as a sequence of feature vectors."""

import numpy as np


def build_trajectory(trace_record, n_points=100):
    """Convert trace events into a sequence of feature vectors.

    Each point in the trajectory is a feature vector summarizing the
    execution state at that moment in time.

    Features per point:
        0: elapsed_fraction (0 to 1)
        1: current_depth (normalized by max_depth)
        2: cumulative_calls_fraction
        3: cumulative_lines_fraction
        4: event_type_indicator (call=1, return=-1, line=0)
        5: function_change (1 if function changed from previous, 0 otherwise)

    Returns ndarray of shape (n_points, 6).
    """
    events = trace_record.events
    if len(events) == 0:
        return np.zeros((n_points, 6))

    total_events = len(events)
    max_depth = max(e.depth for e in events) if events else 1
    max_depth = max(max_depth, 1)  # avoid division by zero

    total_time = events[-1].timestamp if events[-1].timestamp > 0 else 1.0

    # Sample events evenly across the trace
    indices = np.linspace(0, total_events - 1, n_points, dtype=int)

    trajectory = np.zeros((n_points, 6))
    cumulative_calls = 0
    cumulative_lines = 0

    # Pre-compute cumulative counts
    cum_calls = np.zeros(total_events)
    cum_lines = np.zeros(total_events)
    for i, e in enumerate(events):
        if e.event_type == "call":
            cumulative_calls += 1
        elif e.event_type == "line":
            cumulative_lines += 1
        cum_calls[i] = cumulative_calls
        cum_lines[i] = cumulative_lines

    total_calls = max(cumulative_calls, 1)
    total_lines = max(cumulative_lines, 1)

    prev_func = ""
    for j, idx in enumerate(indices):
        e = events[idx]
        trajectory[j, 0] = e.timestamp / total_time  # elapsed fraction
        trajectory[j, 1] = e.depth / max_depth        # normalized depth
        trajectory[j, 2] = cum_calls[idx] / total_calls  # cumulative calls fraction
        trajectory[j, 3] = cum_lines[idx] / total_lines  # cumulative lines fraction

        if e.event_type == "call":
            trajectory[j, 4] = 1.0
        elif e.event_type == "return":
            trajectory[j, 4] = -1.0
        else:
            trajectory[j, 4] = 0.0

        trajectory[j, 5] = 1.0 if e.function_name != prev_func else 0.0
        prev_func = e.function_name

    return trajectory


def trajectory_metrics(trajectory):
    """Compute metrics on a state trajectory.

    Args:
        trajectory: ndarray of shape (n_points, n_features)

    Returns dict of trajectory metrics.
    """
    n_points, n_features = trajectory.shape
    metrics = {}

    # Step-to-step differences
    diffs = np.diff(trajectory, axis=0)
    step_norms = np.linalg.norm(diffs, axis=1)

    # Total path length
    metrics["total_path_length"] = float(np.sum(step_norms))

    # Average step norm
    metrics["mean_step_norm"] = float(np.mean(step_norms)) if len(step_norms) > 0 else 0.0

    # Step norm variance (stability proxy)
    metrics["step_norm_std"] = float(np.std(step_norms)) if len(step_norms) > 0 else 0.0

    # Dispersion: mean distance from centroid
    centroid = np.mean(trajectory, axis=0)
    distances_from_centroid = np.linalg.norm(trajectory - centroid, axis=1)
    metrics["dispersion"] = float(np.mean(distances_from_centroid))

    # End-to-end displacement
    metrics["displacement"] = float(np.linalg.norm(trajectory[-1] - trajectory[0]))

    # Tortuosity: path_length / displacement (how winding the path is)
    if metrics["displacement"] > 1e-10:
        metrics["tortuosity"] = metrics["total_path_length"] / metrics["displacement"]
    else:
        metrics["tortuosity"] = float("inf")

    # Curvature proxy: mean angle change between successive step vectors
    if len(diffs) >= 2:
        angles = []
        for i in range(len(diffs) - 1):
            n1 = np.linalg.norm(diffs[i])
            n2 = np.linalg.norm(diffs[i + 1])
            if n1 > 1e-10 and n2 > 1e-10:
                cos_angle = np.clip(
                    np.dot(diffs[i], diffs[i + 1]) / (n1 * n2), -1.0, 1.0
                )
                angles.append(np.arccos(cos_angle))
        metrics["mean_curvature"] = float(np.mean(angles)) if angles else 0.0
    else:
        metrics["mean_curvature"] = 0.0

    # Recurrence: fraction of points that return close to a previously visited point
    if n_points > 10:
        threshold = np.median(step_norms) * 0.5 if len(step_norms) > 0 else 0.01
        recurrence_count = 0
        # Check every 10th point against earlier trajectory (avoid O(n^2))
        check_indices = range(10, n_points, max(1, n_points // 50))
        for i in check_indices:
            dists = np.linalg.norm(trajectory[:max(1, i - 5)] - trajectory[i], axis=1)
            if np.any(dists < threshold):
                recurrence_count += 1
        metrics["recurrence_rate"] = recurrence_count / max(len(list(check_indices)), 1)
    else:
        metrics["recurrence_rate"] = 0.0

    # Per-feature statistics
    metrics["depth_mean"] = float(np.mean(trajectory[:, 1]))
    metrics["depth_std"] = float(np.std(trajectory[:, 1]))
    metrics["function_change_rate"] = float(np.mean(trajectory[:, 5]))

    return metrics
