import json
import re

from evals.metrics import compute_metrics


# Keyword patterns per tag, derived strictly from the tag definitions, quick reference, and worked examples in docs/TAXONOMY.md.
# Built from taxonomy vocabulary ONLY, never tuned against ground truth labels.

# Known structural limits, by design, not to be fixed by adding keywords:
# - Performance and Marketing collide on "performance"/"performing". The taxonomy splits them on meaning (system vs business outcome), which no keyword can resolve. Expect Performance precision to suffer.
# - Software and Product are relationship distinctions (who owns the thing), not lexical ones. Both lists are weak by necessity. Expect low recall.
# - These failures are the point: they are why the task needs an LLM.

TAG_KEYWORDS = {
    "Security": [
        "unauthorized",
        "breach",
        "breached",
        "vulnerability",
        "vulnerabilities",
        "data exposure",
        "expose",
        "exposed",
        "intrusion",
        "malware",
        "encryption",
        "access attempt",
        "access logs",
        "penetration",
        "credential",
        "credentials",
        "compromised",
    ],
    "Performance": [
        "slow",
        "slowdown",
        "sluggish",
        "lag",
        "lag times",
        "latency",
        "delay",
        "delays",
        "degraded",
        "unresponsive",
        "hinder",
        "overload",
    ],
    "Disruption": [
        "disruption",
        "disruptions",
        "interrupted",
        "interruption",
        "interruptions",
        "outage",
        "outages",
        "downtime",
        "unavailable",
        "unavailability",
        "halt",
        "interfering",
    ],
    "Crash": [
        "crash",
        "crashed",
        "crashes",
        "crashing",
        "failure",
        "failed",
        "fatal",
        "reboot",
        "froze",
        "frozen",
        "stopped running",
    ],
    "Network": [
        "connectivity",
        "firewall",
        "routing",
        "rate limit",
        "rate limits",
        "timeout",
        "cannot connect",
        "unreachable",
        "synchronization",
        "sync",
    ],
    "Feature": [
        "feature",
        "features",
        "enhancement",
        "capability",
        "would like to see",
        "customizable",
        "improvement",
        "improved efficiency",
        "advanced",
    ],
    "Hardware": [
        "hardware",
        "device",
        "devices",
        "server",
        "servers",
        "router",
        "routers",
        "switch",
        "switches",
        "storage array",
        "storage arrays",
        "raid",
        "printer",
        "peripheral",
        "equipment",
    ],
    # Weak by design: tag is about a NAMED tool tied to the issue, not a word.
    "Software": [
        "software",
        "version",
        "update",
        "updates",
        "patch",
        "patches",
        "install",
        "reinstall",
        "compatibility",
        "incompatible",
        "sap",
        "excel",
        "jira",
        "mysql",
        "crm",
    ],
    # Weakest by design: tag is about ownership, no reliable lexical signal.
    "Product": [
        "product",
        "products",
        "acquired",
        "purchased",
        "installation guideline",
        "installation guidelines",
    ],
    "Integration": [
        "integration",
        "integrate",
        "integrating",
        "integrated",
        "api",
        "connect",
        "connection",
        "synchronization",
        "sync",
    ],
    "Marketing": [
        "marketing",
        "campaign",
        "campaigns",
        "brand",
        "brand growth",
        "brand expansion",
        "advertising",
        "lead generation",
        "conversion",
        "crm",
        "digital strategy",
        "digital strategies",
        "target audience",
        "target demographic",
        "ad spending",
        "seo",
    ],
}


def _compile(keywords):
    """Compile each tag's keywords into one word-boundary regex.

    Word-boundary matching (\\b) matches whole words only, so 'net' does not
    match inside 'network' and 'performance' does not match inside 'underperformance'.
    Substring matching would over-fire on fragments.
    """
    compiled = {}
    for tag, words in keywords.items():
        escaped = [re.escape(w) for w in words]
        pattern = r"\b(" + "|".join(escaped) + r")\b"
        compiled[tag] = re.compile(pattern, re.IGNORECASE)
    return compiled


def load_ground_truth(path):
    # Read a vN.jsonl file. Each line is one ticket with subject/body/tags.
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    if not records:
        raise ValueError(f"No records loaded from {path}")
    return records


def predict(records, compiled):
    """Predict tags per ticket by matching keywords against subject + body.

    A ticket matches a tag if any of that tag's patterns appear in the text.
    Multiple tags can match, producing a multi-label prediction.
    """
    predictions = []
    for rec in records:
        text = f"{rec.get('subject', '')} {rec.get('body', '')}"
        matched = [tag for tag, rgx in compiled.items() if rgx.search(text)]
        predictions.append(matched)
    return predictions


def run(gt_path, tags, keywords=TAG_KEYWORDS):
    # Score the keyword baseline. Returns metrics plus empty-prediction count.
    records = load_ground_truth(gt_path)
    compiled = _compile(keywords)
    y_true = [rec["true_tags"] for rec in records]
    y_pred = predict(records, compiled)

    # Tickets where no keyword fired. The baseline predicts nothing for these, guaranteeing a miss. A high count means the vocabulary has blind spots.
    empty = sum(1 for p in y_pred if not p)

    return {
        "metrics": compute_metrics(y_true, y_pred, tags),
        "empty_predictions": empty,
        "n_tickets": len(records),
    }


if __name__ == "__main__":
    import argparse

    import yaml

    parser = argparse.ArgumentParser(description="Keyword baseline.")
    parser.add_argument("--gt", required=True, help="Path to ground truth vN.jsonl")
    parser.add_argument(
        "--taxonomy",
        default="data/taxonomy.yaml",
        help="Path to taxonomy.yaml for the tag list",
    )
    args = parser.parse_args()

    with open(args.taxonomy, encoding="utf-8") as f:
        taxonomy = yaml.safe_load(f)
    tags = taxonomy["tags"]

    result = run(args.gt, tags)
    m = result["metrics"]

    print("\n=== keyword baseline ===")
    print(f"macro_f1:        {m['macro_f1']}   <- decision metric")
    print(f"micro_f1:        {m['micro_f1']}")
    print(f"hamming_loss:    {m['hamming_loss']}")
    print(f"subset_accuracy: {m['subset_accuracy']}")
    print(
        f"\nempty predictions: {result['empty_predictions']} "
        f"of {result['n_tickets']} "
        f"({result['empty_predictions'] / result['n_tickets']:.1%})"
    )
    print("\nper-tag F1:")
    for tag, stats in m["per_tag"].items():
        print(
            f"  {tag:14s} f1={stats['f1']:.3f}  "
            f"p={stats['precision']:.3f}  r={stats['recall']:.3f}  "
            f"support={stats['support']}"
        )
