import hashlib
import json
import logging
from pathlib import Path

import pandas as pd
import yaml
from datasets import load_dataset

logger = logging.getLogger(__name__)

CACHE_PATH = Path(__file__).parent / "cache" / "filtered.parquet"

ALLOWED_QUEUES = {
    "Technical Support",
    "IT Support",
    "Product Support",
    "Service Outages and Maintenance",
}

CONTAMINATION_PREFIXES = (
    "Thank you for contacting us",
    "Would you like",
    "To better understand your",
    "May I assist with your issue regarding",
)

TAG_COLUMNS = [f"tag_{i}" for i in range(1, 9)]


def _load_taxonomy() -> set[str]:
    taxonomy_path = Path(__file__).parent / "taxonomy.yaml"
    with open(taxonomy_path) as file:
        data = yaml.safe_load(file)
    return set(data["tags"])


VALID_TAGS = _load_taxonomy()


# Tag rewrites: map source-dataset tags to canonical taxonomy tags before the trim step drops everything else.
# Each rewrite is documented in docs/DATASET.md with rationale.
TAG_REWRITES = {
    "Firewall": "Network",
    "Software Conflict": "Software",
    "Outage": "Disruption",
    "Sales": "Marketing",
}


def apply_tag_rewrites(tags: list[str]) -> list[str]:
    """Rewrite source tags to canonical taxonomy tags.
    Deduplicates after rewrite since two source tags can map to one canonical tag."""
    rewritten = [TAG_REWRITES.get(t, t) for t in tags]
    # dedupe preserving order
    seen = set()
    out = []
    for t in rewritten:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def load() -> pd.DataFrame:
    if CACHE_PATH.exists():
        logger.info("Loading from cache. Delete %s to rebuild.", CACHE_PATH)
        return pd.read_parquet(CACHE_PATH)

    logger.info("Downloading dataset")
    dataset = load_dataset("Tobi-Bueck/customer-support-tickets", split="train")
    df = dataset.to_pandas()

    df["body"] = df["body"].str.replace(r"\n", "\n", regex=False)
    df["subject"] = df["subject"].str.replace(r"\n", "\n", regex=False)

    df["ticket_id"] = range(len(df))
    logger.info("Raw rows: %d", len(df))

    # Filter 1: English only
    df = df[df["language"] == "en"]
    logger.info("After language filter: %d", len(df))

    # Filter 2: IT queues only
    df = df[df["queue"].isin(ALLOWED_QUEUES)]
    logger.info("After queue filter: %d", len(df))

    # Filter 3: Drop null-body rows
    df = df[df["body"].notna()].copy()
    logger.info("After null body filter: %d ", len(df))

    # Filter 4: Drop contamination, fill NaN bodies with empty string for the filter
    mask = df["body"].fillna("").str.startswith(CONTAMINATION_PREFIXES)
    removed = df[mask][["ticket_id", "subject", "body"]]
    removed.to_json(
        CACHE_PATH.parent / "contamination_removed.jsonl",
        orient="records",
        lines=True,
        force_ascii=False,
    )
    df = df[~mask]
    logger.info("After contamination filter: %d (removed %d)", len(df), len(removed))

    # Filter 5: Deduplicate on (subject, body) hash
    df["content_hash"] = df.apply(
        lambda row: hashlib.md5(
            json.dumps([row["subject"], row["body"]], ensure_ascii=False).encode()
        ).hexdigest(),
        axis=1,
    )
    df = df.drop_duplicates(subset=["content_hash"])
    logger.info("After deduplication: %d", len(df))

    # Reshape: melt tag_1 to tag_8 into a single tags column
    melted = (
        df[["ticket_id"] + TAG_COLUMNS]
        .melt(id_vars=["ticket_id"], value_vars=TAG_COLUMNS, value_name="tags")
        .dropna(subset=["tags"])
    )

    tags_per_ticket = (melted.groupby("ticket_id")["tags"]).apply(list).reset_index()

    df = df.drop(columns=TAG_COLUMNS).merge(tags_per_ticket, on="ticket_id")

    # Filter 6a: rewrite source tags to canonical taxonomy tags
    df["tags_before"] = df["tags"]
    df["tags"] = df["tags"].apply(apply_tag_rewrites)
    df["rewritten"] = df["tags_before"] != df["tags"]
    logger.info(
        "After tag rewrites: %d tickets actually changed", int(df["rewritten"].sum())
    )

    # Filter 6b: trim to 11 tag taxonomy
    df["tags"] = df["tags"].apply(
        lambda tags: [tag for tag in tags if tag in VALID_TAGS]
    )
    logger.info("After taxonomy trim: %d", len(df))

    # Filter 7: drop zero tag tickets
    df = df[df["tags"].apply(len) > 0]
    logger.info("After zero tag drop: %d", len(df))

    # Write rewrites trace for spot-check targeting and verification
    df[df["rewritten"]][["ticket_id", "tags_before", "tags"]].to_json(
        CACHE_PATH.parent / "rewrites_applied.jsonl",
        orient="records",
        lines=True,
        force_ascii=False,
    )

    # Drop helper columns and reorder
    df = df[["ticket_id", "subject", "body", "type", "queue", "priority", "tags"]]

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CACHE_PATH, index=False)
    logger.info("Saved to cache")

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = load()
    print(f"Final dataset: {len(df)} rows")
    print(df.head())
