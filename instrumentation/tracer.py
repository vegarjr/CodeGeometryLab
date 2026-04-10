"""Execution trace instrumentation via sys.settrace.

Captures function calls, returns, line executions, and timing
without requiring modification of variant source code.
"""

import sys
import time
import threading
from dataclasses import dataclass, field


@dataclass
class TraceEvent:
    step: int
    event_type: str          # "call", "return", "line"
    function_name: str
    filename: str
    lineno: int
    depth: int
    timestamp: float         # monotonic seconds since trace start
    parent_function: str = ""


@dataclass
class TraceRecord:
    variant_name: str
    events: list = field(default_factory=list)
    wall_clock_s: float = 0.0
    function_call_counts: dict = field(default_factory=dict)
    max_call_depth: int = 0
    total_lines_executed: int = 0
    total_calls: int = 0
    total_returns: int = 0
    unique_functions: set = field(default_factory=set)

    was_capped: bool = False

    def to_dict(self):
        return {
            "variant_name": self.variant_name,
            "wall_clock_s": self.wall_clock_s,
            "total_events": len(self.events),
            "total_calls": self.total_calls,
            "total_returns": self.total_returns,
            "total_lines_executed": self.total_lines_executed,
            "max_call_depth": self.max_call_depth,
            "unique_function_count": len(self.unique_functions),
            "function_call_counts": dict(self.function_call_counts),
            "was_capped": self.was_capped,
        }


class ExecutionTracer:
    """Lightweight tracer that captures execution events via sys.settrace."""

    def __init__(self, variant_name, target_file=None, max_events=2_000_000):
        self.variant_name = variant_name
        self.target_file = target_file
        self.max_events = max_events
        self._record = TraceRecord(variant_name=variant_name)
        self._step = 0
        self._depth = 0
        self._start_time = 0.0
        self._call_stack = []
        self._capped = False

    def _trace_fn(self, frame, event, arg):
        # Only trace events from the target variant file
        filename = frame.f_code.co_filename
        if self.target_file and self.target_file not in filename:
            return self._trace_fn

        func_name = frame.f_code.co_name
        now = time.monotonic() - self._start_time

        if event == "call":
            parent = self._call_stack[-1] if self._call_stack else ""
            self._call_stack.append(func_name)
            self._depth = len(self._call_stack)

            if self._depth > self._record.max_call_depth:
                self._record.max_call_depth = self._depth

            self._record.total_calls += 1
            self._record.unique_functions.add(func_name)
            self._record.function_call_counts[func_name] = (
                self._record.function_call_counts.get(func_name, 0) + 1
            )

            if not self._capped:
                self._record.events.append(TraceEvent(
                    step=self._step,
                    event_type="call",
                    function_name=func_name,
                    filename=filename,
                    lineno=frame.f_lineno,
                    depth=self._depth,
                    timestamp=now,
                    parent_function=parent,
                ))
                self._step += 1
                if self._step >= self.max_events:
                    self._capped = True
                    self._record.was_capped = True

        elif event == "return":
            self._record.total_returns += 1
            if self._call_stack:
                self._call_stack.pop()
            self._depth = len(self._call_stack)

            if not self._capped:
                self._record.events.append(TraceEvent(
                    step=self._step,
                    event_type="return",
                    function_name=func_name,
                    filename=filename,
                    lineno=frame.f_lineno,
                    depth=self._depth + 1,
                    timestamp=now,
                ))
                self._step += 1
                if self._step >= self.max_events:
                    self._capped = True
                    self._record.was_capped = True

        elif event == "line":
            self._record.total_lines_executed += 1

            if not self._capped:
                self._record.events.append(TraceEvent(
                    step=self._step,
                    event_type="line",
                    function_name=func_name,
                    filename=filename,
                    lineno=frame.f_lineno,
                    depth=self._depth,
                    timestamp=now,
                ))
                self._step += 1
                if self._step >= self.max_events:
                    self._capped = True
                    self._record.was_capped = True

        return self._trace_fn

    def trace(self, fn, *args, **kwargs):
        """Execute fn under tracing and return (result, TraceRecord)."""
        self._start_time = time.monotonic()
        old_trace = sys.gettrace()
        sys.settrace(self._trace_fn)
        try:
            result = fn(*args, **kwargs)
        finally:
            sys.settrace(old_trace)
        self._record.wall_clock_s = time.monotonic() - self._start_time
        return result, self._record


def trace_variant(variant_name, compute_fn, params, target_file=None, max_events=2_000_000):
    """Convenience function: trace a single variant execution.

    Returns (result_array, TraceRecord).
    """
    tracer = ExecutionTracer(
        variant_name=variant_name,
        target_file=target_file,
        max_events=max_events,
    )
    return tracer.trace(compute_fn, **params)


def benchmark_variant(variant_name, compute_fn, params, n_runs=30):
    """Run a variant n_runs times and collect wall-clock timing statistics.

    Returns dict with timing stats (no tracing overhead).
    """
    times = []
    for _ in range(n_runs):
        t0 = time.monotonic()
        compute_fn(**params)
        t1 = time.monotonic()
        times.append(t1 - t0)

    import numpy as np
    times = np.array(times)
    return {
        "variant_name": variant_name,
        "n_runs": n_runs,
        "mean_s": float(np.mean(times)),
        "std_s": float(np.std(times)),
        "min_s": float(np.min(times)),
        "max_s": float(np.max(times)),
        "median_s": float(np.median(times)),
        "all_times_s": times.tolist(),
    }
