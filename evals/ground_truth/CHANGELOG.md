# Ground truth changelog

Taxonomy and filter changes are recorded here. A change may bump the taxonomy version without producing a new ground truth file, ground truth versions track data regenerations.

## v4

### Taxonomy

- Dropped Documentation. 12 tags down to 11. The source applied Documentation to ~26% of tickets (3810 post-trim), the dominant noise source flagged in the v2 spot check. To test whether a clean doc-request subset could be salvaged, an allowlist-gated strip rule was built (keep Documentation only on an explicit written artifact request paired with request framing). It stripped 84% of Documentation labels: Request 69.3%, Incident 99.2%, Problem 98.2%, Change 93.5%. Sampling both the kept and stripped partitions showed the surviving ~16% is lexically inseparable from fix-requests and advice-requests. All three use identical request phrasing (provide, supply, instructions, details, steps), and separation was near coin-flip even on Request-type tickets where doc asks should concentrate. A per-tag F1 against coin-flip ground truth is meaningless and would drag the macro average. Removed as not reliably learnable from intake text. This is a label-quality limit of the synthetic data, not a modelling choice. On real intake data where customers distinguish "send me the docs" from "fix my problem," the class may be recoverable. The strip rule was the investigation tool only and was deleted from load_dataset.py, not shipped as trim logic. TagEnum, taxonomy.yaml, TAXONOMY.md, DATASET.md updated in the same commit.

- v3 was never shipped. v3 was a planned Documentation-definition tightening, a strip rule gated on a genuine-doc-request allowlist. Building that rule was the investigation above, which showed the tag unsalvageable. No v3.jsonl was generated and no v3 corpus exists. The tightening path was superseded by this full drop. The taxonomy version is retained as v4 to match the already committed value; ground truth files skip from v2.jsonl to a future v4.jsonl with no v3.jsonl. The gap is intentional and recorded here so it does not read as a missing file.

- Versioning rule corrected. TAXONOMY.md previously stated taxonomy version and ground truth version move together as a single counter. v3 broke that: a definition-only change that produced no ground truth file. The rule now reads: taxonomy version tracks definition changes, ground truth version tracks data regenerations, related but not lockstep. taxonomy.yaml version field bumped from 2 to 4 to match TAXONOMY.md, from which it had drifted. The field is documentation only and is not read by code (the loader consumes the tag list, not the version).

### Corpus filters

- Null-body filter added (Filter 3). Drops rows with an empty body before contamination matching. Removes 1 ticket (17893 to 17892). Added during the v4 Documentation investigation and kept. It renumbered the downstream filters, contamination is now Filter 4, dedup Filter 5, zero-tag drop Filter 6.

- Zero-tag loss rose from 2.48% (under the 13-tag taxonomy) to 4.3% (652 of 15047 post-dedup). Expected and attributable to the Documentation drop. Documentation-only tickets now trim to zero tags and fall out at the final filter. The post-dedup corpus itself barely moved, so the change in final count comes from this zero-tag fallout, not from the null-body filter (which removed a single row).

- Current cascade, per the DATASET.md row-count table: raw 61765, language 28261, queue 17893, null-body 17892, contamination 17878, dedup 15047, zero-tag drop 14395 final. The rewrite step modified tags on 3604 tickets and does not change the row count.

- CHANGELOG reconciliation. The v2 entry below records an earlier filter state (contamination 17879, dedup 15048, 14685 final) from before the null-body filter existed. Those numbers do not match the current cascade and are left unchanged: v2.jsonl is immutable and its entry describes the corpus at v2 tag time. The current numbers are the ones above and in DATASET.md. From v4 forward every filter change is recorded here at the version it ships in.

### Ground truth

- No new ground truth file in this commit. v2.jsonl predates the Documentation drop and still carries Documentation labels, so it is stale against the v4 taxonomy. A v4.jsonl regeneration against the 14395 corpus is the next milestone and must land before any eval run.

- Per-tag floors do not carry forward from v2. The tag set changed (11 tags, Documentation removed), so floors recalibrate against the first measured LLM baseline at week 5.

### Open flags (backlog, not blocking v4)

- Contamination filter catches 14 tickets. An earlier wider-pattern estimate put it near 100. The current prefixes are deliberately narrow: the greedy "Customer support has documented" prefix was removed in v2 because it deleted genuine customer incident tickets. The ~86 difference may still sit in the corpus. Backlog: widen prefixes without re-introducing those false positives.

- DATASET.md tag-distribution tables and priority percentages are marked stale and gated "do not cite" pending recomputation against the 14395 corpus. This is tomorrow's work along with the v4.jsonl regeneration.

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
