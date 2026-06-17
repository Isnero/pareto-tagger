"""Unit tests for evals.metrics.
Expected values hand-computed from the TP/FP/FN definitions, not produced by the code under test."""

import math
import pytest
from evals.metrics import compute_metrics


def approx(a, b):
    return math.isclose(a, b, abs_tol=1e-4)


def test_perfect_prediction():
    tags = ["A", "B"]
    y_true = [["A"], ["A", "B"], ["B"]]
    y_pred = [["A"], ["A", "B"], ["B"]]
    m = compute_metrics(y_true, y_pred, tags)
    assert approx(m["macro_f1"], 1.0)
    assert approx(m["micro_f1"], 1.0)
    assert approx(m["hamming_loss"], 0.0)
    assert approx(m["subset_accuracy"], 1.0)


def test_one_missed_tag():
    tags = ["A", "B"]
    y_true = [["A", "B"]]
    y_pred = [["A"]]
    m = compute_metrics(y_true, y_pred, tags)
    assert approx(m["macro_f1"], 0.5)
    assert approx(m["micro_f1"], 0.6667)
    assert approx(m["hamming_loss"], 0.5)
    assert approx(m["subset_accuracy"], 0.0)
    assert m["per_tag"]["B"]["recall"] == 0.0
    assert m["per_tag"]["B"]["support"] == 1


def test_macro_micro_diverge_on_imbalance():
    # Same predictions two stories. Common is frequent and perfect, rare is infrequent and missed. This is the reason macro is the gate.
    tags = ["Common", "Rare"]
    y_true = [["Common"], ["Common"], ["Common"], ["Common", "Rare"]]
    y_pred = [["Common"], ["Common"], ["Common"], ["Common"]]
    m = compute_metrics(y_true, y_pred, tags)
    assert approx(m["macro_f1"], 0.5)  # Rare drags it down
    assert approx(m["micro_f1"], 0.8889)  # Common dominates the pool
    assert m["macro_f1"] < m["micro_f1"]


def test_macro_over_support_only():
    tags = ["A", "B", "C"]
    y_true = [["A"]]
    y_pred = [["A"]]
    full = compute_metrics(y_true, y_pred, tags)
    only = compute_metrics(y_true, y_pred, tags, macro_over_support_only=True)
    assert approx(full["macro_f1"], 1 / 3)  # B and C absent count as 0
    assert approx(only["macro_f1"], 1.0)  # only A averaged


def test_false_positive_penalised():
    tags = ["A", "B"]
    y_true = [["A"]]
    y_pred = [["A", "B"]]  # B is a false alarm
    m = compute_metrics(y_true, y_pred, tags)
    assert m["per_tag"]["B"]["precision"] == 0.0
    assert m["per_tag"]["A"]["f1"] == 1.0
    assert approx(m["subset_accuracy"], 0.0)


def test_length_mismatch_raises():
    with pytest.raises(ValueError, match="Length mismatch"):
        compute_metrics([["A"]], [["A"], ["B"]], ["A", "B"])


def test_empty_raises():
    with pytest.raises(ValueError, match="Empty"):
        compute_metrics([], [], ["A", "B"])


def test_unknown_tag_raises():
    with pytest.raises(ValueError, match="outside taxonomy"):
        compute_metrics([["A"]], [["Z"]], ["A", "B"])
