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
