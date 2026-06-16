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


def compute_metrics(y_true, y_pred, tags, macro_over_supprt_only=False):
    """Multi-label metrics. Returns a dict with macro_f1 first.
    y_true, y_pred: equal-length lists of tag-name lists, aligned by ticket.
    tags: the taxonomy, an ordered list of valid tag names.
    macro_over_support_only: if True, macro averages only over tags with support > 0 in y_true.
    Use on slices or small samples where some tags are absent, so an absent tag does not drag macro to 0.
    Default False averages over all tags, correct for the full eval set where every tag appears.
    """

    if len(y_true) != len(y_pred):
        raise ValueError(f"Length mismatch: {len(y_true)} true vs {len(y_pred)} pred")
    if not y_true:
        raise ValueError("Empty input")

    counts = _counts(y_true, y_pred, tags)

    per_tag = {}
    for t in tags:
        p, r, f = _prf(counts[t]["tp"], counts[t]["fp"], counts[t]["fn"])
        per_tag[t] = {
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f, 4),
            "support": counts[t]["support"],
        }

    # Macro - unweighted mean of per-tag F1.
    if macro_over_supprt_only:
        f1s = [per_tag[t]["f1"] for t in tags if per_tag[t]["support"] > 0]
    else:
        f1s = [per_tag[t]["f1"] for t in tags]
    macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0

    # Micro - pool every count then one P/R/F1.
    tp = sum(counts[t]["tp"] for t in tags)
    fp = sum(counts[t]["fp"] for t in tags)
    fn = sum(counts[t]["fn"] for t in tags)
    _, _, micro_f1 = _prf(tp, fp, fn)

    # Hamming loss - fraction of (ticket, tag) pairs predicted incorrectly.
    n_cells = len(y_true) * len(tags)
    wrong_cells = sum(counts[t]["fp"] + counts[t]["fn"] for t in tags)
    hamming = wrong_cells / n_cells if n_cells else 0.0

    # Subset accuracy - fraction of tickets where predicted set == true set
    exact = sum(
        1
        for true_row, pred_row in zip(y_true, y_pred)
        if set(true_row) == set(pred_row)
    )
    subset_acc = exact / len(y_true) if y_true else 0.0

    return {
        "macro_f1": round(macro_f1, 4),
        "micro_f1": round(micro_f1, 4),
        "hamming_loss": round(hamming, 4),
        "subset_accuracy": round(subset_acc, 4),
        "n_tickets": len(y_true),
        "per_tag": per_tag,
    }
