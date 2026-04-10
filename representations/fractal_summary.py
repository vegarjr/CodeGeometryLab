"""Representation C: Recursive / fractal summary of execution traces.

Analyzes branching structure, motif repetition, self-similarity,
and compression characteristics.
"""

import numpy as np
import zlib
from collections import Counter


def _encode_trace_string(trace_record):
    """Encode trace events as a compact string for compression analysis."""
    symbols = []
    for e in trace_record.events:
        if e.event_type == "call":
            symbols.append(f"C{e.function_name[:8]}d{e.depth}")
        elif e.event_type == "return":
            symbols.append(f"R{e.function_name[:8]}d{e.depth}")
        elif e.event_type == "line":
            symbols.append(f"L{e.lineno}")
    return "|".join(symbols)


def compression_ratio(trace_record):
    """Compute compression ratio of the trace string.

    Higher compression = more repetitive/self-similar structure.
    """
    trace_str = _encode_trace_string(trace_record)
    if not trace_str:
        return 0.0
    raw_bytes = trace_str.encode("utf-8")
    compressed = zlib.compress(raw_bytes, level=9)
    return len(compressed) / len(raw_bytes)


def _extract_ngrams(sequence, n):
    """Extract n-grams from a sequence."""
    return [tuple(sequence[i:i + n]) for i in range(len(sequence) - n + 1)]


def motif_analysis(trace_record, ngram_sizes=(3, 5, 8)):
    """Analyze repeated motifs in the event sequence.

    A motif is a repeated subsequence of event types.
    Returns metrics about motif reuse at different scales.
    """
    # Build event type sequence
    event_seq = []
    for e in trace_record.events:
        if e.event_type == "call":
            event_seq.append(f"C:{e.function_name}")
        elif e.event_type == "return":
            event_seq.append(f"R:{e.function_name}")
        elif e.event_type == "line":
            event_seq.append(f"L:{e.lineno}")

    results = {}
    for n in ngram_sizes:
        if len(event_seq) < n:
            results[f"motif_{n}_unique_ratio"] = 1.0
            results[f"motif_{n}_top_frequency"] = 0
            results[f"motif_{n}_entropy"] = 0.0
            continue

        ngrams = _extract_ngrams(event_seq, n)
        counts = Counter(ngrams)
        total = len(ngrams)
        unique = len(counts)

        # Unique ratio: 1.0 = all unique (no repetition), low = high repetition
        results[f"motif_{n}_unique_ratio"] = unique / total if total > 0 else 1.0

        # Top motif frequency
        results[f"motif_{n}_top_frequency"] = counts.most_common(1)[0][1] if counts else 0

        # Motif entropy (Shannon)
        probs = np.array(list(counts.values())) / total
        entropy = -np.sum(probs * np.log2(probs + 1e-15))
        results[f"motif_{n}_entropy"] = float(entropy)

    return results


def branching_profile(trace_record):
    """Analyze the branching/depth structure of the execution.

    Returns metrics about how the execution tree branches over time.
    """
    depths = [e.depth for e in trace_record.events if e.event_type in ("call", "return")]
    if not depths:
        return {
            "depth_transitions": 0,
            "depth_range": 0,
            "mean_depth": 0.0,
            "depth_entropy": 0.0,
            "branching_growth_rate": 0.0,
        }

    depths = np.array(depths)
    depth_changes = np.diff(depths)

    # Count depth transitions (direction changes in depth)
    transitions = 0
    for i in range(1, len(depth_changes)):
        if depth_changes[i] != 0 and np.sign(depth_changes[i]) != np.sign(depth_changes[i - 1]):
            transitions += 1

    # Depth distribution entropy
    depth_counts = Counter(depths.tolist())
    total = len(depths)
    probs = np.array(list(depth_counts.values())) / total
    depth_entropy = -np.sum(probs * np.log2(probs + 1e-15))

    # Branching growth: how fast does max depth grow in the first half vs second half
    half = len(depths) // 2
    if half > 0:
        first_half_max = np.max(depths[:half])
        second_half_max = np.max(depths[half:])
        growth_rate = (second_half_max - first_half_max) / max(first_half_max, 1)
    else:
        growth_rate = 0.0

    return {
        "depth_transitions": int(transitions),
        "depth_range": int(np.max(depths) - np.min(depths)),
        "mean_depth": float(np.mean(depths)),
        "depth_entropy": float(depth_entropy),
        "branching_growth_rate": float(growth_rate),
    }


def self_similarity_score(trace_record, scales=(2, 4, 8)):
    """Estimate self-similarity by comparing trace patterns at different scales.

    Divides the trace into segments at each scale and measures how similar
    segments are to each other using normalized edit distance on event types.
    """
    event_types = [e.event_type[0] for e in trace_record.events]  # 'c', 'r', 'l'
    n = len(event_types)
    if n < 16:
        return {"self_similarity_mean": 0.0, "self_similarity_std": 0.0}

    similarities_all = []

    for scale in scales:
        seg_len = n // scale
        if seg_len < 4:
            continue

        segments = []
        for i in range(scale):
            start = i * seg_len
            end = start + seg_len
            segments.append(tuple(event_types[start:end]))

        # Compare all pairs using simple match fraction
        similarities = []
        for i in range(len(segments)):
            for j in range(i + 1, len(segments)):
                matches = sum(a == b for a, b in zip(segments[i], segments[j]))
                similarities.append(matches / seg_len)

        if similarities:
            similarities_all.extend(similarities)

    if similarities_all:
        return {
            "self_similarity_mean": float(np.mean(similarities_all)),
            "self_similarity_std": float(np.std(similarities_all)),
        }
    return {"self_similarity_mean": 0.0, "self_similarity_std": 0.0}


def fractal_metrics(trace_record):
    """Compute all fractal/self-similarity metrics for a trace."""
    metrics = {}
    metrics["compression_ratio"] = compression_ratio(trace_record)
    metrics.update(motif_analysis(trace_record))
    metrics.update(branching_profile(trace_record))
    metrics.update(self_similarity_score(trace_record))
    return metrics
