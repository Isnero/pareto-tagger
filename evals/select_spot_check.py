import json
import random
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


GROUND_PATH = Path(__file__).parent / "ground_truth" / "v2.jsonl"
OUTPUT_PATH = Path(__file__).parent / "ground_truth" / "spot_check_v2.md"
REPO_ROOT = Path(__file__).parent.parent
SEED = 67
SAMPLE_SIZE = 30


def main() -> None:
    with open(GROUND_PATH) as file:
        rows = [json.loads(line) for line in file]

    random.seed(SEED)
    spot_check = random.sample(rows, SAMPLE_SIZE)

    lines = [
        "# Spot check, v2 ground truth",
        "",
        f"Random seed: {SEED}",
        f"Sample size: {SAMPLE_SIZE}",
        f"Source: {GROUND_PATH.relative_to(REPO_ROOT).as_posix()}",
        "Reviewer: ks",
        "",
        "## Results",
        "",
        "- Agree: ",
        "- Partial: ",
        "- Disagree: ",
        "- Per-ticket issue rate: ",
        "",
        "## Per-ticket notes",
        "",
    ]

    for row in spot_check:
        lines.extend(
            [
                f"### ticket_id {row['ticket_id']}",
                "",
                f"**Subject:** {row['subject']}",
                "",
                "**Body:**",
                "",
                "```text",
                row["body"],
                "```",
                "",
                f"**Priority:** {row['priority']} | **Queue:** {row['queue']} | **Type:** {row['type']}",
                "",
                f"**Current true_tags:** {row['true_tags']}",
                "",
                "**Verdict:** ",
                "",
                "**Notes:** ",
                "",
                "---",
                "",
            ]
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s with %d tickets", OUTPUT_PATH, SAMPLE_SIZE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
