# Ground truth changelog

Records what changed between ground truth versions and why. Each `vN.jsonl` is immutable once tagged. Taxonomy changes, filter changes, and label changes all create a new version.

## v2

### Taxonomy

- Merged Sales into Marketing. 13 tags down to 12. Source labels did not distinguish the two consistently (the same intake template appeared tagged Sales on one ticket and Marketing on a near-identical other), making the boundary unlearnable. Applied via TAG_REWRITES (Sales maps to Marketing). TagEnum, taxonomy.yaml, TAXONOMY.md, and DATASET.md updated in the same commit.
- Tightened Documentation definition with a negative clause: closing boilerplate ("let me know if you need more details", "please advise on next steps") does not count as a documentation request. Definition change only. Source labels cannot be retroactively fixed, but spot-check reviewers now mark boilerplate-only Documentation tags as errors.

### Corpus filters

- Tag rewrites added (Filter 5): Firewall to Network, Software Conflict to Software, Outage to Disruption. Compatibility to Integration was considered and rejected after manual review showed roughly half of Compatibility tickets were software or hardware faults, not integration.
- Contamination filter (Filter 3) tightened: removed the "Customer support has documented" prefix from the match set. It was too greedy and was deleting 10-14 genuine customer incident tickets that merely opened with that phrase. Final removed set is 14 unambiguous agent-reply tickets.
- Filter count progression: language 28261, queue 17893, contamination 17879 (14 removed), dedup 15048, taxonomy trim and zero-tag drop 14685 final. Supersedes the v1 locked corpus of 14612.
- 3604 tickets had tags modified by the rewrites, mostly Outage-to-Disruption folding. Net zero-tag recovery is small (tens of tickets). Disruption is now broader and higher frequency after absorbing Outage.

### Ground truth

- v2.jsonl regenerated: 500 stratified records (v1 was 515). The drop is mechanical. Folding Outage into Disruption and Sales into Marketing collapses separate per-tag sampling buckets before set-dedup, so fewer unique tickets survive the per-tag draw.
- Per-tag floors do NOT carry from v1 to v2. Disruption broadened (absorbed Outage), Marketing broadened (absorbed Sales). Floors recalibrate against the first measured LLM baseline (week 5).
- Seeds: stratified sample SEED 67, spot-check seed 67.

### Verification

- Firewall-to-Network and Software-Conflict-to-Software folds verified manually against rewrites_applied.jsonl. Sampled rewritten tickets and confirmed the fold produces the intended tag. This verifies the rewrite mechanism (the transformation fires correctly), not the formal label-quality spot-check (a reviewer agreeing the resulting tags are right given the text). The random-30 spot-check does not include rewritten tickets, so those two folds are checked at the mechanism level only. Considered sufficient for v2 given the folds are clean and unambiguous. Targeting in select_spot_check.py deferred.

### Known tag-quality notes (v2)

- Documentation (151 occurrences) is both high-frequency and high-noise. Source labels apply it to closing boilerplate ("let me know if you need more details") on incident tickets that contain no actual documentation request. The tightened definition in TAXONOMY.md lets spot-check reviewers mark these as errors, but the source labels themselves are not retroactively fixed. Because Documentation is high-frequency, its noise drags micro F1 (frequency-weighted) more than a noisy tail tag would. Expect the week-5 micro floor to calibrate lower partly because of this. Flagged for v3 review: candidate to restrict to intake-only documentation requests, or to drop like Bug if noise stays high after spot-check.
- Marketing (63 occurrences) is the smallest tag after the Sales fold and is now the tail. At this class size, per-tag F1 has the widest standard error, so its floor will be the loosest and its measured number the noisiest. This is expected, not a defect.

## v1

- Initial ground truth. 515 stratified records sampled from the filtered corpus (14612 tickets after six filters).
- 13-tag taxonomy: Security, Performance, Disruption, Crash, Network, Documentation, Feature, Hardware, Software, Product, Integration, Marketing, Sales.
- Labels inherited from the source dataset, trimmed to taxonomy. No row-level manual relabeling. Quality validated by a 30-ticket spot check (40% per-ticket issue rate, consistent with the 56% baseline from the original 50-ticket review).
- Stratified sample SEED 67, up to 40 tickets per tag.
