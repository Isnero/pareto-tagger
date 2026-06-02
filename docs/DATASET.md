# Dataset

## Source

- Dataset: [Tobi-Bueck/customer-support-tickets](https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets) on HuggingFace
- License: CC BY-NC 4.0 (non-commercial). Portfolio use only.
- Citation: Bueck, T. (2025). Multilingual Customer Support Tickets (Synthetic). Generated with the Open Ticket AI Synthetic Data Generator.

## Pipeline

The loader applies row filters and tag operations in a fixed order in `data/load_dataset.py`. Row filters drop tickets. Tag operations rewrite or trim the tag set and do not drop rows on their own, except indirectly: a ticket whose tags are all trimmed away is removed by the final zero-tag drop.

### Row filters

1. `language == 'en'` (drops the German half)
2. `queue IN ('Technical Support', 'IT Support', 'Product Support', 'Service Outages and Maintenance')` (keeps pure-IT queues)
3. Drop null-body rows
4. Drop support-agent reply contamination
5. Dedup on `(subject, body)` hash
6. Drop tickets with zero kept tags (runs after the tag operations below)

### Tag operations

Applied between dedup and the zero-tag drop:

- Rewrite source tags to canonical taxonomy tags (`apply_tag_rewrites`, includes Sales to Marketing)
- Trim to the 11-tag taxonomy in `docs/TAXONOMY.md`

### Row counts

Counts from the current pipeline run. Each row follows from the one above it.

| Step | Tickets remaining |
| --- | --- |
| Raw rows | 61765 |
| After language filter | 28261 |
| After queue filter | 17893 |
| After null-body filter | 17892 |
| After contamination filter | 17878 |
| After deduplication | 15047 |
| After zero-tag drop | 14395 |

The tag rewrite and trim steps are not in this table because they do not change the row count. The rewrite step changed the tag set on 3604 tickets. The trim step leaves the row count unchanged; its effect appears only when a trimmed ticket reaches zero tags and is dropped at the final step.

Final corpus: **14395 tickets**.

### Filter 4: support-agent reply contamination

Some tickets are not customer messages but support agent replies asking for clarification. Examples found in the original sample review:

- "Thank you for contacting us. To better understand your request, could you please provide details on..."
- "Would you like assistance with digital strategies? I can provide detailed information..."
- "Customer support has documented system interruptions impacting..."

These contaminate both training and evaluation. The model would learn to predict tags for messages that have nothing to do with the actual ticket content.

Filter pattern (pandas `str.startswith` on a tuple of prefixes in `load_dataset.py`):

```sql
NOT (
  body LIKE 'Thank you for contacting us%'
  OR body LIKE 'Would you like%'
  OR body LIKE 'To better understand your%'
  OR body LIKE 'Customer support has documented%'
)
```

The current prefix set removes 14 tickets. An earlier wider-pattern estimate put this nearer 100; the current rules are narrower and only match the confirmed agent-reply openers. Tickets that slip past these prefixes are logged as iteration backlog. Removed tickets are written to `contamination_removed.jsonl` for audit.

### Filter 5: deduplication

The dataset contains exact duplicate tickets. The original zero-tag investigation found pairs of identical entries (lead generation tracking, data analytics solutions). Either the synthetic generator emitted duplicates or the dataset preparation has a bug. Dedup uses an MD5 hash of `(subject, body)`.

### Filter 6: zero-tag drop

After the taxonomy trim, tickets with no remaining valid tag are dropped. With the 11-tag taxonomy this removes 652 tickets, **4.3% of the post-dedup corpus** (652 of 15047). They split into two groups:

- Tickets whose original labels were entirely workflow tags, the redundant trio (IT, Tech Support, Technical), or Feedback. Mostly off-topic content like investment advice questions or pure marketing strategy chatter.
- Tickets whose only valid tag was Documentation, now dropped (see Documentation removal below).
- Legitimate IT tickets where the labeller used very specific tail tags (Elasticsearch, RAID-Controller, Dashboard) and skipped the general categories. Real losses, but the alternative is expanding the taxonomy with rare tags that cannot be reliably learned at this volume.

The loss rose from 2.48% (in the earlier 13-tag taxonomy) to 4.3% specifically because Documentation-only tickets now fall out. That is expected: those tickets were carried solely by a tag shown to be unlearnable from intake text.

## Documentation removal (v4)

Documentation was in the taxonomy through v3 and was removed in v4 after a corpus-wide analysis showed it could not be cleanly separated from other intents.

### The investigation

The source labels apply Documentation to roughly 26% of all tickets (3810 of the post-trim corpus). A v2 spot check first flagged it as the dominant noise source. Documentation was repeatedly attached to Incident and Problem tickets that report a malfunction and ask for a fix, not for a document.

To test whether a clean subset could be salvaged, an allowlist-gated rule was built: keep Documentation only when the body contains an explicit written-artifact request (documentation, specification, system requirements, API docs, guide, manual) paired with request framing. The rule stripped Documentation from 84% of its rows. The per-type breakdown:

| Ticket type | Documentation labels | Stripped | Strip rate |
| --- | --- | --- | --- |
| Request | 1852 | 1284 | 69.3% |
| Incident | 983 | 975 | 99.2% |
| Problem | 607 | 596 | 98.2% |
| Change | 368 | 344 | 93.5% |

### The finding

Both partitions were sampled and read. The genuine ~16% kept by the rule was not clean, and the 84% stripped was not uniformly wrong. The reason is lexical: in this corpus, genuine documentation requests and fix-requests and advice-requests all use identical phrasing. "Could you supply comprehensive instructions for integrating with MongoDB" (a real doc request) and "offer a remedy or steps to restore the missing data" (a crash report) share the same request-for-procedure shape and the same verbs (provide, supply, instructions, information, details, steps). No keyword rule separates them.

The separation failed even on Request-type tickets, where documentation requests should concentrate. Sampling the stripped Request rows showed roughly a coin flip between genuine doc asks and advice or pre-sales inquiries using the same words.

### The decision

Documentation dropped. A tag whose genuine instances are lexically inseparable from noise cannot produce reliable ground truth, and a per-tag F1 computed against coin-flip labels is meaningless and would drag the macro average. The class adds no discriminating signal beyond the substantive tags (Security, Crash, Performance, Integration) it co-occurs with in nearly every case.

This is a label-quality limit of the synthetic data, not a modelling choice. On real intake data where customers more clearly distinguish "send me the docs" from "fix my problem," a documentation-request class may be recoverable.

## Tag distribution

Computed against the v4 corpus of 14395 tickets. 25500 total tag instances.

| Tag | Frequency | % of all tag instances |
| --- | --- | --- |
| Performance | 6810 | 26.71% |
| Disruption | 3862 | 15.15% |
| Security | 3618 | 14.19% |
| Feature | 2512 | 9.85% |
| Network | 2247 | 8.81% |
| Crash | 1363 | 5.35% |
| Marketing | 1217 | 4.77% |
| Product | 1195 | 4.69% |
| Hardware | 1050 | 4.12% |
| Integration | 838 | 3.29% |
| Software | 788 | 3.09% |

Performance dominates at 26.71%, more than double the next tag. The set is heavily skewed toward a few high-frequency classes. Eval calibration should weight macro and per-tag F1 over micro, since a classifier can score well on micro by handling Performance alone.

### Tags per ticket

| Tags per ticket | Tickets | % |
| --- | --- | --- |
| 1 | 6304 | 43.79% |
| 2 | 5534 | 38.44% |
| 3 | 2134 | 14.82% |
| 4 | 389 | 2.70% |
| 5 | 34 | 0.24% |

Average 1.77 tags per ticket, down from 1.89 under the 13-tag taxonomy. The drop follows from folding Outage into Disruption and Sales into Marketing (two tags collapse to one on co-tagged tickets) and from removing Documentation. 99.8% of tickets carry 1 to 4 tags. The classifier prompt asks for 1 to 4 with a hard cap of 5, which fits.

There is no zero-tag row: zero-tag tickets are dropped at Filter 6 before the corpus is written. The 4.3% zero-tag loss is documented in the Filter 6 section.

## Label noise estimate

### Methodology

50 tickets sampled at random from the filtered dataset. Each tag on each ticket reviewed manually against subject and body. Verdict per ticket recorded as agree, partial, or disagree.

### Results

- Agree: 22/50
- Partial (one or two tags wrong or missing): 21/50
- Disagree (multiple tags wrong, or core tag missing): 7/50

Per-ticket issue rate: 56% (28/50 tickets had at least one questionable tag).
Per-tag noise estimate: roughly 15 to 20% (rough, not measured tag-by-tag).

The two numbers measure different things. Per-ticket counts any ticket with one bad tag as noisy. Per-tag counts individual mismatches against total tag assignments. The per-tag number is what affects model training directly. The per-ticket number is the more conservative talking point.

Note: this 50-ticket baseline predates the Documentation removal. The single largest driver of per-ticket noise was Documentation, so the post-v4 per-ticket rate is expected to be lower. Regenerate the spot-check noise estimate against the v4 corpus before citing a current figure.

### Tags removed from taxonomy and why

| Tag | Reason |
| ----- | -------- |
| IT, Tech Support, Technical | Redundant trio. After IT-queue filter, all three appear on roughly half of tickets and add no signal beyond the queue field |
| Feedback | Inconsistent meaning. Applied to requests, problem reports, and observations interchangeably. Reviewers cannot agree on what it means, so a model cannot learn it |
| Resolution, Recovery, Investigation, Fix, Communication, Assistance, Guidance | Workflow or resolution-derived. Describe what the support team does, not what the customer reports. Often not in the body at all |
| Bug | Overloaded. Applied to software defects, marketing strategy failures, and security incidents. No consistent semantic |
| Virus | Diagnosed post-hoc, low frequency |
| Outage | Nested inside Disruption (every Outage is a Disruption but not vice versa). Kept Disruption because it covers more cases |
| Maintenance | Workflow tag, often refers to actions taken not problem reported |
| Sales | Merged into Marketing in v2. Source labels did not separate the two consistently, the boundary was unlearnable |
| Documentation | Removed in v4. Genuine documentation requests are lexically inseparable from fix-requests and advice-requests in this corpus. See Documentation removal above |
| All long-tail tags below 0.5% frequency | Insufficient data for per-tag F1 to be meaningful |

### Tags retained

11 tags: Security, Performance, Disruption, Crash, Network, Feature, Hardware, Software, Product, Integration, Marketing.

Full per-tag definitions and worked examples in `docs/TAXONOMY.md`.

## Why the answer field is not used

The dataset includes an `answer` column considered for expanding the taxonomy back. Hypothesis: tags like Bug, Recovery, Maintenance might be predictable from resolution text even if absent from the customer-facing subject and body.

Sample inspection of 50 random tickets showed the `answer` column is inconsistent. Some entries contain resolution text. Others contain clarifying questions back to the customer ("Could you provide more details on..."). Others contain call-back offers ("We can take this on the call to answer your questions"). Not a reliable signal source.

Decision: subject and body only. The model predicts what the customer reported, not what was found during investigation. This matches the intake-triage use case and keeps the input length predictable.

If real ServiceNow data ever becomes available, work_notes and resolution_notes are richer signals than this synthetic answer field.

## Priority distribution

In the filtered corpus: 48.7% high, 37.9% medium, 13.4% low. The skew is a synthetic-data artifact. Because high covers about half the data, it is not a meaningful slice cut. Eval slicing uses low (13%) instead.

## Ground truth labeling workflow

Ground truth uses inherited labels from the source dataset, trimmed to the taxonomy by `data/load_dataset.py`. No manual re-labeling at the row level. Quality is validated by spot checks (see `evals/ground_truth/`). The per-ticket issue rate from the spot check is the headline noise measurement.

Per-row labeling fields (`labelled_by`, `labelled_at`, `review_notes`) are present in the schema but unpopulated. They are reserved for a future version if a full manual labeling pass is done.

## Synthetic data caveat

Tickets are LLM-generated and mostly clean, but not uniformly. Some bodies contain truncated or half-finished sentences, an artifact of the generator. Defects this dataset largely lacks, and that real production tickets carry heavily:

- Typos and grammatical errors
- Mixed languages within one body
- Log paste-ins
- Urgency words ("URGENT", "ASAP", "P1") without justification
- Customer-system-name inconsistency

The honest read: this dataset is cleaner than production but not pristine. It shows the pipeline works on near-clean inputs. Whether the same prompts and taxonomy hold on heavily noisy production data is not answered here.
