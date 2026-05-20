import hashlib
import json

from pathlib import Path

import pandas as pd
from datasets import load_dataset

CACHE_PATH = Path(__file__).parent / "cache" / "filtered.parquet"

VALID_TAGS = {
    "Security",
    "Performance",
    "Disruption",
    "Crash",
    "Network",
    "Documentation",
    "Feature",
    "Hardware",
    "Software",
    "Product",
    "Integration",
    "Marketing",
    "Sales",
}

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
    "Customer support has documented",
)

TAG_COLUMNS = [f"tag_{i}" for i in range(1, 9)]


def load() -> pd.DataFrame:
    if CACHE_PATH.exists():
        print("Loading from cache")
        return pd.read_parquet(CACHE_PATH)

    print("Downloading dataset")
    dataset = load_dataset("Tobi-Bueck/customer-support-tickets", split="train")
    df = dataset.to_pandas()

    df["ticket_id"] = range(len(df))
    print(f"Raw rows: {len(df)}")

    # Filter 1: English only
    df = df[df["language"] == "en"]
    print(f"After language filter: {len(df)}")

    # Filter 2: IT queues only
    df = df[df["queue"].isin(ALLOWED_QUEUES)]
    print(f"After queue filter: {len(df)}")

    # Filter 3: Drop contamination
    mask = df["body"].str.startswith(CONTAMINATION_PREFIXES)
    df = df[~mask]
    print(f"After contamination filter: {len(df)}")

    # Filter 4: Deduplicate on (subject, body) hash
    df["content_hash"] = df.apply(
        lambda row: hashlib.md5(
            json.dumps([row["subject"], row["body"]], ensure_ascii=False).encode()
        ).hexdigest(),
        axis=1,
    )
    df = df.drop_duplicates(subset=["content_hash"])
    print(f"After deduplication: {len(df)}")

    # Reshape: melt tag_1 to tag_8 into a single tags column
    melted = (
        df[["ticket_id"] + TAG_COLUMNS]
        .melt(id_vars=["ticket_id"], value_vars=TAG_COLUMNS, value_name="tags")
        .dropna(subset=["tags"])
    )

    tags_per_ticket = (melted.groupby("ticket_id")["tags"]).apply(list).reset_index()

    df = df.drop(columns=TAG_COLUMNS).merge(tags_per_ticket, on="ticket_id")

    # Filter 5: trim to 13 tag taxonomy
    df["tags"] = df["tags"].apply(
        lambda tags: [tag for tag in tags if tag in VALID_TAGS]
    )

    # Filter 6: drop zero tag tickets
    df = df[df["tags"].str.len() > 0]
    print(f"After taxonomy trim and zero tag drop: {len(df)}")

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CACHE_PATH, index=False)
    print("Saved to cache")

    return df
