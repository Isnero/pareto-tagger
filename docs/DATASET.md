# Dataset

## Source

- Dataset: [Tobi-Bueck/customer-support-tickets](https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets) on HuggingFace
- License: CC BY-NC 4.0 (non-commercial). Portfolio use only.
- Citation: Bueck, T. (2025). Multilingual Customer Support Tickets (Synthetic). Generated with the Open Ticket AI Synthetic Data Generator.

## Filters applied

Six filters in `data/load_dataset.py`, applied in order:

1. `language = 'en'` (drops the German half)
2. `queue IN ('Technical Support', 'IT Support', 'Product Support', 'Service Outages and Maintenance')` (keeps pure-IT queues)
3. Drop support-agent reply contamination
4. Dedup on `(subject, body)` hash
5. Trim tags to the 13-tag taxonomy in `docs/TAXONOMY.md`
6. Drop tickets with zero kept tags after trim

| Step | Tickets remaining |
| --- | --- |
| Raw English tickets | ~30,000 |
| After queue filter | 17,893 |
| After contamination filter (~100 dropped) | ~17,793 |
| After dedup | TBD at implementation |
| After taxonomy trim and zero-tag drop (~443 dropped) | ~16,500 |

### Filter 3: support-agent reply contamination

Some tickets in the dataset are not customer messages but support agent replies asking for clarification. Examples found in the 50-ticket sample review:

- "Thank you for contacting us. To better understand your request, could you please provide details on..."
- "Would you like assistance with digital strategies? I can provide detailed information..."
- "Customer support has documented system interruptions impacting..."

These contaminate both training and evaluation. The model would learn to predict tags for messages that have nothing to do with the actual ticket content.

Filter pattern (DuckDB SQL form, translated to pandas in `load_dataset.py`):

```sql
NOT (
  body LIKE 'Thank you for contacting us%'
  OR body LIKE 'Would you like%'
  OR body LIKE 'To better understand your%'
  OR body LIKE 'Customer support has documented%'
)
```

A spot count showed around 100 such tickets out of 17,893. Less than 1% but worth removing for clean ground truth.

### Filter 4: deduplication

The dataset contains exact duplicate tickets. The 10-ticket investigation of zero-tag tickets found two pairs of identical entries (lead generation tracking, data analytics solutions). Either the synthetic generator emitted duplicates or the dataset preparation has a bug.

Dedup uses a hash of `(subject, body)`. Final count documented at implementation.

### Filter 6: zero-tag drop

After taxonomy trim, around 443 tickets (2.48%) have no tags from the 13-tag taxonomy. These split into two groups:

- Tickets where the original labels were entirely workflow tags or the redundant trio (IT, Tech Support, Technical) plus Feedback. Mostly off-topic content like investment advice questions or pure marketing strategy chatter.
- Legitimate IT tickets where the labeller used very specific tail tags (Elasticsearch, RAID-Controller, Dashboard) and skipped the general categories. These are real losses but the alternative would be to expand the taxonomy with rare tags that cannot be reliably learned at this volume.

Both groups dropped. Documented as 2.48% data loss for cleaner ground truth.

## Tag distribution in raw data

Before any filtering or trimming. Useful as historical reference for taxonomy decisions.

Tag completeness: 100% of tickets have at least one tag. Average 4.99 tags per ticket.

Top 25 tags by frequency, post-queue-filter:

| Tag | Frequency | % of all tag instances |
| ----- | ----------- | ------------------------ |
| Tech Support | 9,884 | 11.08% |
| IT | 9,752 | 10.93% |
| Performance | 8,474 | 9.50% |
| Bug | 5,587 | 6.26% |
| Feedback | 4,720 | 5.29% |
| Documentation | 4,477 | 5.02% |
| Security | 4,253 | 4.77% |
| Disruption | 3,340 | 3.74% |
| Feature | 3,252 | 3.64% |
| Outage | 2,983 | 3.34% |
| Network | 2,701 | 3.03% |
| Technical | 2,562 | 2.87% |
| Resolution | 1,782 | 2.00% |
| Crash | 1,534 | 1.72% |
| Recovery | 1,425 | 1.60% |
| Product | 1,380 | 1.55% |
| Guidance | 1,192 | 1.34% |
| Hardware | 1,152 | 1.29% |
| Sales | 1,083 | 1.21% |
| Maintenance | 868 | 0.97% |
| Integration | 845 | 0.95% |
| Software | 770 | 0.86% |
| Incident | 644 | 0.72% |
| Support | 578 | 0.65% |
| Marketing | 564 | 0.63% |

## Tag distribution after taxonomy trim

After trimming to the 13-tag taxonomy (see `docs/TAXONOMY.md`):

| Tags per ticket | Tickets | % |
| --- | --- | --- |
| 0 | 443 | 2.48% |
| 1 | 5,664 | 31.65% |
| 2 | 7,868 | 43.97% |
| 3 | 3,296 | 18.42% |
| 4 | 574 | 3.21% |
| 5 | 47 | 0.26% |
| 6 | 1 | 0.01% |

Average: 1.89 tags per ticket. 99.5% of tickets have between 1 and 4 tags. The classifier prompt asks for 1 to 4 tags with a hard cap of 5, which fits this distribution.

## Label noise estimate

### Methodology

50 tickets sampled at random from the filtered dataset. Each tag on each ticket reviewed manually against subject and body. Verdict per ticket recorded as agree, partial, or disagree.

### Results

- Agree: 22/50
- Partial (one or two tags wrong or missing): 21/50
- Disagree (multiple tags wrong, or core tag missing): 7/50

**Per-ticket issue rate: 56%** (28/50 tickets had at least one questionable tag).

**Per-tag noise estimate: roughly 15 to 20%** (rough, not measured tag-by-tag).

The two numbers measure different things. Per-ticket counts any ticket with one bad tag as "noisy". Per-tag counts individual mismatches against total tag assignments. The per-tag number is what affects model training directly. The per-ticket number is the more conservative talking point for documentation.

### Tags removed from taxonomy and why

| Tag | Reason |
| ----- | -------- |
| IT, Tech Support, Technical | Redundant trio. After IT-queue filter, all three appear on roughly half of tickets and add no signal beyond the queue field |
| Feedback | Inconsistent meaning. Applied to requests, problem reports, and observations interchangeably. Reviewers cannot agree on what it means, so a model cannot learn it |
| Resolution, Recovery, Investigation, Fix, Communication, Assistance, Guidance | Workflow or resolution-derived. Describe what the support team does, not what the customer reports. Often not in the body at all |
| Bug | Overloaded. Applied to software defects, marketing strategy failures, and security incidents. No consistent semantic |
| Virus | Diagnosed post-hoc, low frequency |
| Outage | Nested inside Disruption (every Outage is a Disruption but not vice versa). Kept Disruption because it covers more cases. Dropping Outage avoids redundant tag pairs |
| Maintenance | Workflow tag, often refers to actions taken not problem reported |
| All long-tail tags below 0.5% frequency | Insufficient data for per-tag F1 to be meaningful |

### Tags retained

13 tags: Security, Performance, Disruption, Crash, Network, Documentation, Feature, Hardware, Software, Product, Integration, Marketing, Sales.

Sales was added back after the zero-tag investigation showed 7 of 10 zero-tag tickets were sales or marketing content where Sales was the right tag. Without it, those tickets had nothing to predict.

Full per-tag definitions and worked examples in `docs/TAXONOMY.md`.

## Why the answer field is not used

The dataset includes an `answer` column that I considered using to expand the taxonomy back. Hypothesis: tags like Bug, Recovery, Maintenance might be predictable from resolution text even if absent from the customer-facing subject and body.

Sample inspection of 50 random tickets showed the `answer` column is inconsistent. Some entries contain resolution text. Others contain clarifying questions back to the customer ("Could you provide more details on..."). Others contain call-back offers ("We can take this on the call to answer your questions"). Not a reliable signal source.

Decision: subject and body only. The model predicts what the customer reported, not what was found during investigation. This matches the intake-triage use case and keeps the input length predictable.

If real ServiceNow data ever becomes available, work_notes and resolution_notes are richer signals than this synthetic answer field.

## Synthetic data caveat

Tickets are LLM-generated. Real production tickets contain noise that this dataset does not have:

- Typos and grammatical errors
- Mixed languages within one body
- Log paste-ins
- Half-finished sentences
- Urgency words ("URGENT", "ASAP", "P1") without justification
- Customer-system-name inconsistency (one ticket calls it "the prod DB", the next calls it "primary database")

The classification pipeline is designed to be data-source-agnostic. When real data is available, the same pipeline runs against it through configuration only.

The honest read: this dataset proves the pipeline works on clean inputs. The harder question of whether the same prompts and taxonomy hold up on noisy production data is not answered here.
