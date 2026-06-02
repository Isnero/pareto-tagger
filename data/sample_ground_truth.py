import logging
from pathlib import Path

import pandas as pd

from data.load_dataset import load, VALID_TAGS

logger = logging.getLogger(__name__)


JSONL_PATH = Path(__file__).parent.parent / "evals" / "ground_truth" / "v4.jsonl"


def generate_ground_truth() -> pd.DataFrame:
    df = load()

    df_exploded = df.explode("tags")

    # Set to store unique ticket IDs for the ground truth set - using a set to avoid duplicates when sampling across multiple tags
    sampled_ids = set()

    # For each tag, sample up to 40 tickets, storing their IDs in the set
    for tag in VALID_TAGS:
        tag_tickets = df_exploded[df_exploded["tags"] == tag]
        sample_size = min(40, len(tag_tickets))
        picked = tag_tickets.sample(n=sample_size, random_state=67)
        sampled_ids.update(picked["ticket_id"].tolist())

    # Checking if we have enough samples, if not, filling with random tickets from the remaining pool
    remaining = df[~df["ticket_id"].isin(sampled_ids)]
    shortfall = 500 - len(sampled_ids)
    if shortfall > 0:
        filler = remaining.sample(n=shortfall, random_state=67)
        sampled_ids.update(filler["ticket_id"].tolist())

    ground_truth = df[df["ticket_id"].isin(sampled_ids)]

    logger.info("Length of sampled_ids: %d", len(sampled_ids))
    logger.info("Ground truth shape: %s", ground_truth.shape)
    return ground_truth


def save_to_jsonl(df: pd.DataFrame) -> None:
    if JSONL_PATH.exists():
        raise FileExistsError(
            f"{JSONL_PATH} exists. Ground truth is immutable, bump the version."
        )

    df = df.copy()
    df = df.rename(columns={"tags": "true_tags"})
    df["sampled_at"] = pd.Timestamp.now().strftime("%Y-%m-%d")
    df["labelled_by"] = "ks"
    df["labelled_at"] = None
    df["review_notes"] = None
    df["slice_tags"] = df.apply(
        lambda row: (
            (["short"] if len(row["body"]) < 200 else [])
            + (["long"] if len(row["body"]) > 600 else [])
            + (["low_priority"] if row["priority"] == "low" else [])
        ),
        axis=1,
    )

    JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(JSONL_PATH, orient="records", lines=True)
    logger.info("Saved %d ground truth records to %s", len(df), JSONL_PATH)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = generate_ground_truth()
    save_to_jsonl(df)
