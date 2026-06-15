"""Multi-label classification metrics for the pareto-tagger eval harness.

Pure functions over predicted and true tag sets. No I/O, no model calls, no
sklearn. Built from the TP/FP/FN counts directly so the harness owns its
numbers and they map onto the definitions in docs/EVALS.md.

Macro F1 is the primary decision metric. Micro is dominated by the few high
frequency tags (Performance alone is ~27% of tag instances, see DATASET.md),
so a model can post a strong micro while failing the long tail. Macro weights
every tag equally and is what the CI gate should read.

The caller supplies the tag list. This module does not hardcode the taxonomy,
so there is no second source of truth to drift from taxonomy.yaml and the
TagEnum. run_eval.py sources the tag list from the same place the schema does.
"""

from __future__ import annotations


def _counts(y_true, y_pred, tags):
    # Per-tag TP, FP, FN over the dataset. support is TP + FN.
    tag_set = set(tags)
    counts = {t: {"tp": 0, "fp": 0, "fn": 0} for t in tags}
    for true_row, pred_row in zip(y_true, y_pred):
        true_s = set(true_row)
        pred_s = set(pred_row)
        unknown = (true_s | pred_s) - tag_set
        if unknown:
            raise ValueError(f"Tags outside taxonomy: {sorted(unknown)}")
        for t in tags:
            in_true = t in true_s
            in_pred = t in pred_s
            if in_true and in_pred:
                counts[t]["tp"] += 1
            elif in_pred and not in_true:
                counts[t]["fp"] += 1
            elif in_true and not in_pred:
                counts[t]["fn"] += 1
    for t in tags:
        counts[t]["support"] = counts[t]["tp"] + counts[t]["fn"]
    return counts


def _prf(tp, fp, fn):
    # Precision, recall, F1 from counts. Zero denominators yield 0.0.
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    )
    return precision, recall, f1
