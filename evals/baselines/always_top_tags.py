import json
from collections import Counter

from evals.metrics import compute_metrics


def load_ground_truth(path):
    # Read a vN.jsonl file. Each line is one ticket with a true_tags list.
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    if not records:
        raise ValueError(f"No records found in {path}")
    return records


def rank_tags_by_frequency(records):
    # Return tag names ordered most to least frequent in the ground truth.
    counter = Counter()
    for rec in records:
        counter.update(rec["true_tags"])
    return [tag for tag, _ in counter.most_common()]


def predict_top_n(records, ranked_tags, n):
    # "Predict" the same top-n tags for every ticket. Text is ignored.
    top_n = ranked_tags[:n]
    return [list(top_n) for _ in records]


def run(gt_path, tags, n_values=(1, 2, 3)):
    # Score the always-top-N baseline for each N. Returns {n: metrics}.
    records = load_ground_truth(gt_path)
    y_true = [rec["true_tags"] for rec in records]
    ranked = rank_tags_by_frequency(records)

    results = {}
    for n in n_values:
        y_pred = predict_top_n(records, ranked, n)
        results[n] = {
            "predicted_tags": ranked[:n],
            "metrics": compute_metrics(y_true, y_pred, tags),
        }
    return results


if __name__ == "__main__":
    import argparse
    import yaml

    parser = argparse.ArgumentParser(description="Always-top-N baseline.")
    parser.add_argument("--gt", required=True, help="Path to ground truth vN.jsonl")
    parser.add_argument(
        "--taxonomy",
        default="data/taxonomy.yaml",
        help="Path to taxonomy.yaml for the tag list",
    )
    parser.add_argument(
        "--n",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="N values to sweep, e.g. --n 1 2 3",
    )
    args = parser.parse_args()

    with open(args.taxonomy, encoding="utf-8") as f:
        taxonomy = yaml.safe_load(f)
    tags = taxonomy["tags"]

    results = run(args.gt, tags, n_values=tuple(args.n))

    for n, payload in results.items():
        m = payload["metrics"]
        print(f"\n=== always_top_{n} | predicts {payload['predicted_tags']} ===")
        print(f"macro_f1:        {m['macro_f1']}   <- decision metric")
        print(f"micro_f1:        {m['micro_f1']}")
        print(f"hamming_loss:    {m['hamming_loss']}")
        print(f"subset_accuracy: {m['subset_accuracy']}")
