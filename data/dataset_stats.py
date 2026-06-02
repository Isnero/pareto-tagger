"""Compute the distribution tables in docs/DATASET.md from the cached corpus.

Rerun after any corpus change (taxonomy or filter edit) that regenerates the parquet,
then paste the output into the Tag distribution and Priority sections of DATASET.md.
The counts in this docstring (14395 rows, 11 tags, v4) are the state at last run and will change with the taxonomy version.

Reads data/cache/filtered.parquet and prints markdown-ready tables for:
  1. Tag frequency (post-trim)
  2. Tags-per-ticket distribution (1..N) with counts and percentages
  3. Average tags per ticket
  4. Priority distribution

Run from repo root:  python -m data.dataset_stats
"""

from data.load_dataset import load


def main() -> None:
    df = load()
    n = len(df)
    print(f"Corpus: {n} tickets\n")

    # 1. Tag frequency, post-trim
    exploded = df.explode("tags")
    tag_counts = exploded["tags"].value_counts()
    total_instances = int(tag_counts.sum())

    print("## Tag frequency (post-trim, 11 tags)\n")
    print(f"Total tag instances: {total_instances}\n")
    print("| Tag | Frequency | % of all tag instances |")
    print("| --- | --- | --- |")
    for tag, count in tag_counts.items():
        pct = 100 * count / total_instances
        print(f"| {tag} | {count} | {pct:.2f}% |")
    print()

    # 2. Tags-per-ticket distribution
    tags_per = df["tags"].apply(len)
    dist = tags_per.value_counts().sort_index()

    print("## Tags per ticket\n")
    print("| Tags per ticket | Tickets | % |")
    print("| --- | --- | --- |")
    for k, count in dist.items():
        pct = 100 * count / n
        print(f"| {k} | {count} | {pct:.2f}% |")
    print()

    # 3. Average tags per ticket
    avg = tags_per.mean()
    print(f"Average tags per ticket: {avg:.2f}")
    # share with 1..4 tags, the band the prompt targets
    band = tags_per.between(1, 4).sum()
    print(f"Tickets with 1-4 tags: {band} ({100 * band / n:.1f}%)\n")

    # 4. Priority distribution
    print("## Priority distribution\n")
    prio = df["priority"].value_counts()
    print("| Priority | Tickets | % |")
    print("| --- | --- | --- |")
    for p, count in prio.items():
        pct = 100 * count / n
        print(f"| {p} | {count} | {pct:.2f}% |")


if __name__ == "__main__":
    main()
