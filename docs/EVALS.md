# Evals

## Baselines

Baselines set the floor a real classifier must clear. They establish whether the LLM approach earns its complexity and cost. A classifier that cannot beat a text-blind baseline is not worth running.

Macro F1 is the primary decision metric. Micro is dominated by the few high-frequency tags (Performance is ~27% of tag instances), so a model can post a strong micro while failing the long tail. See DATASET.md for the distribution.

All numbers below are scored against ground truth v4.jsonl (500 stratified records, 11-tag taxonomy).

### always-top-N (text-blind frequency baseline)

Predicts the N most frequent tags for every ticket. Ignores ticket text entirely. This is the dignity floor: the real classifier must clear it or the pipeline is broken.

| N | Predicted tags | Macro F1 | Micro F1 | Hamming loss | Subset acc |
| --- | --- | --- | --- | --- | --- |
| 1 | Performance | 0.0556 | 0.2808 | 0.2049 | 0.0380 |
| 2 | Performance, Disruption | 0.0964 | 0.3532 | 0.2431 | 0.0580 |
| 3 | Performance, Disruption, Feature | 0.1262 | 0.3607 | 0.2984 | 0.0060 |

Dignity floor: macro F1 0.126 (N=3). The real classifier must beat this.

Notes:

- Macro sits far below micro at every N. The blind baseline scores roughly triple on micro because Performance owns most instance counts, while macro punishes the eight to nine tags the baseline never predicts. This is the macro-micro divergence that motivates macro as the gate.
- Subset accuracy drops at N=3 (0.006) below N=1 and N=2. Adding a tag to every prediction breaks more exact-set matches than it creates, since most tickets do not carry Feature. Subset accuracy is brittle under fixed-set prediction and is not an optimization target.
- This floor is inflated by label noise. Ground truth carries a ~30% per-ticket issue rate (see DATASET.md spot check), biased toward over-applying Performance and Disruption, the exact tags this baseline predicts. The blind baseline gets a tailwind from the same defect that inflates the labels. Beating 0.126 is necessary, not impressive. The keyword baseline sets the meaningful bar.
- Top-3 here is Performance, Disruption, Feature. Corpus distribution in DATASET.md ranks Security third, not Feature. The difference is the stratified sample, which boosts rare tags and flattens the head, so sample tag ranking does not match corpus ranking. This is a sample-vs-corpus artifact, not a bug. Sample ranking, not corpus ranking, is what these baselines score against.

### keyword baseline (text-blind regex matching)

Predicts tags by word-boundary regex matching against subject + body. Keyword lists derived strictly from tag definitions and worked examples in TAXONOMY.md, built blind to the ground truth labels and frozen before scoring. Not tuned to lift the number. This is the bar a real classifier must clear to justify reading context instead of matching words.

| Metric | Value |
| --- | --- |
| Macro F1 | 0.5233 |
| Micro F1 | 0.5124 |
| Hamming loss | 0.1958 |
| Subset accuracy | 0.1020 |
| Empty predictions | 33 / 500 (6.6%) |

Per-tag F1:

| Tag | F1 | Precision | Recall | Support |
| --- | --- | --- | --- | --- |
| Security | 0.778 | 0.935 | 0.667 | 87 |
| Crash | 0.726 | 0.640 | 0.838 | 68 |
| Disruption | 0.613 | 0.863 | 0.476 | 145 |
| Marketing | 0.558 | 0.410 | 0.873 | 63 |
| Integration | 0.557 | 0.396 | 0.940 | 67 |
| Hardware | 0.530 | 0.404 | 0.770 | 74 |
| Network | 0.510 | 0.629 | 0.429 | 91 |
| Software | 0.417 | 0.268 | 0.936 | 78 |
| Feature | 0.366 | 0.591 | 0.265 | 98 |
| Product | 0.350 | 0.477 | 0.276 | 76 |
| Performance | 0.349 | 0.873 | 0.218 | 220 |

Bar to beat: macro F1 0.523. The real classifier must clear this.

Reading the result. The macro is propped up by over-firing on four tags, not by discrimination. Software, Integration, Marketing, and Hardware all post recall above 0.77 with precision below 0.45. They match on words that saturate an IT support corpus:

- Software fires on "update", "version", "install"
- Integration on "api", "connect"
- Marketing on "crm", "campaign"

These catch nearly every true instance (high recall) and misfire on many others (low precision). The F1 stays high because the harmonic mean still rewards runaway recall. This is an honest property of taxonomy-derived keywords on this corpus, not a bug, and the lists were left frozen rather than tuned down.
The two patterns that confirm the floor is working:

- Performance: precision 0.873, recall 0.218. The opposite of over-firing. The baseline catches only the Performance tickets using its specific vocabulary (slow, lag, sluggish), missing the 78% described in other words, but what it does predict is almost always right. The feared Performance-Marketing collision did not fire, because "performance"/"performing" was deliberately kept out of the Performance keyword list, so Marketing tickets do not trip it.
- Contextual tags score low. Product (F1 0.350) and Feature (F1 0.366) are defined by situation and ownership, not signature words, and keyword matching cannot see that. This is exactly the space an LLM has to earn its cost in.

Comparison to always-top floor:

| Baseline | Macro F1 | Micro F1 |
| --- | --- | --- |
| always-top (N=3) | 0.126 | 0.361 |
| keyword | 0.523 | 0.512 |

Reading the text quadruples macro over the text-blind baseline, confirming the corpus carries real lexical signal. Note macro and micro are now close (0.523 vs 0.512), unlike always-top where micro was triple macro. The keyword baseline spreads its predictions across all tags rather than concentrating on the frequent few, so the two averages converge.

Both baselines are scored against noisy ground truth (~30% per-ticket issue rate, biased toward Performance/Disruption over-tagging). The noise caps every achievable F1: a classifier cannot perfectly match labels that are themselves ~30% wrong. Keep this ceiling next to any reported number.
