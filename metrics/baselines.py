"""Baseline metrics for comparison: static code analysis, trivial trace stats."""

import ast
import importlib
import inspect
import textwrap


def _get_source(module_path):
    """Get source code of a variant module."""
    mod = importlib.import_module(module_path)
    return inspect.getsource(mod)


def line_count(module_path):
    """Count non-empty, non-comment lines."""
    source = _get_source(module_path)
    lines = source.split("\n")
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith('"""'):
            count += 1
    return count


def ast_node_count(module_path):
    """Count total AST nodes."""
    source = _get_source(module_path)
    tree = ast.parse(source)
    count = 0
    for _ in ast.walk(tree):
        count += 1
    return count


def cyclomatic_complexity(module_path):
    """Estimate cyclomatic complexity (sum across all functions).

    Counts decision points: if, elif, for, while, and, or, except, with, assert.
    """
    source = _get_source(module_path)
    tree = ast.parse(source)
    complexity = 1  # base complexity

    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.IfExp)):
            complexity += 1
        elif isinstance(node, ast.For):
            complexity += 1
        elif isinstance(node, ast.While):
            complexity += 1
        elif isinstance(node, ast.And):
            complexity += 1
        elif isinstance(node, ast.Or):
            complexity += 1
        elif isinstance(node, ast.ExceptHandler):
            complexity += 1
        elif isinstance(node, ast.With):
            complexity += 1
        elif isinstance(node, ast.Assert):
            complexity += 1

    return complexity


def function_count(module_path):
    """Count function/method definitions."""
    source = _get_source(module_path)
    tree = ast.parse(source)
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            count += 1
    return count


def class_count(module_path):
    """Count class definitions."""
    source = _get_source(module_path)
    tree = ast.parse(source)
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            count += 1
    return count


def max_nesting_depth(module_path):
    """Estimate maximum nesting depth of control flow."""
    source = _get_source(module_path)
    tree = ast.parse(source)

    def _depth(node, current=0):
        max_d = current
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                max_d = max(max_d, _depth(child, current + 1))
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                max_d = max(max_d, _depth(child, current + 1))
            else:
                max_d = max(max_d, _depth(child, current))
        return max_d

    return _depth(tree)


def compute_all_baselines(module_path):
    """Compute all baseline metrics for a variant module."""
    return {
        "baseline_line_count": line_count(module_path),
        "baseline_ast_node_count": ast_node_count(module_path),
        "baseline_cyclomatic_complexity": cyclomatic_complexity(module_path),
        "baseline_function_count": function_count(module_path),
        "baseline_class_count": class_count(module_path),
        "baseline_max_nesting_depth": max_nesting_depth(module_path),
    }


def compute_trace_baselines(trace_record):
    """Trivial trace statistics (baselines for geometric metrics)."""
    return {
        "baseline_trace_total_events": len(trace_record.events),
        "baseline_trace_total_calls": trace_record.total_calls,
        "baseline_trace_total_lines": trace_record.total_lines_executed,
        "baseline_trace_max_depth": trace_record.max_call_depth,
        "baseline_trace_unique_functions": len(trace_record.unique_functions),
        "baseline_trace_wall_clock": trace_record.wall_clock_s,
    }
