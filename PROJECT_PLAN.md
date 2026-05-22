# LLM-powered classifier system

Multi-label tag classifier for IT support tickets with Pareto report generation.

---

## Table of contents

1. [Problem](#problem)
2. [Dataset](#dataset)
3. [Classification approach](#classification-approach)
4. [System architecture](#system-architecture)
5. [Tech stack](#tech-stack)
6. [Repository structure](#repository-structure)
7. [Evaluation methodology](#evaluation-methodology)
8. [Weekly plan, 12 weeks](#weekly-plan-12-weeks)
9. [What I deliberately do not build](#what-i-deliberately-do-not-build)
10. [Monthly budget](#monthly-budget)
11. [Risks and contingencies](#risks-and-contingencies)
12. [Iteration plan after completion](#iteration-plan-after-completion)

---

## Problem

IT operations teams analyse closed incidents periodically to find recurring issues and direct automation effort at the largest sources of toil. The classic Pareto 80/20 analysis. The work is painful for two reasons.

Manual categorisation is slow. Someone reads each ticket and assigns relevant tags. For 500 to 2000 tickets per month this takes days.

Categorisation is inconsistent. Different analysts tag the same ticket differently. The resulting data is noisy and the Pareto report becomes a moving target.

The system here accepts a CSV ticket export, runs each ticket through an LLM with a closed taxonomy and structured outputs, and produces a Pareto report with charts and insights. Operation cost and quality metrics are tracked, gated by an evaluation harness in CI.

What makes this more than a notebook demo:

- The taxonomy is closed and validated. No hallucinated tags.
- Async processing, structured outputs, observability, retries, caching, and cost tracking are all present.
- The evaluation harness uses versioned ground truth, per-tag F1 floors, and measured baselines. CI blocks merges when quality regresses.
- Cost, latency, and reliability are first-class. The system is cheap to run, the LLM call path is observable, and failures degrade gracefully.

---

## Dataset

Source: Tobi-Bueck/customer-support-tickets on HuggingFace, CC BY-NC 4.0. Synthetic, multilingual customer support tickets.

After all filters the working dataset is around 16,500 tickets. Filters applied in order:

1. `language = 'en'`
2. `queue IN ('Technical Support', 'IT Support', 'Product Support', 'Service Outages and Maintenance')`
3. Drop support-agent reply contamination (`body LIKE 'Thank you for contacting us%'` and similar patterns, around 100 tickets)
4. Dedup on `(subject, body)` hash (count TBD at implementation)
5. Trim tags to 13-tag taxonomy
6. Drop tickets with zero kept tags after trim (around 443 tickets, 2.48%)

Full noise analysis, taxonomy reasoning, and filter rationale in `docs/DATASET.md`. Tag definitions and edge cases in `docs/TAXONOMY.md`.

---

## Classification approach

Single-stage multi-label classification. The model predicts between 1 and 4 tags from the closed 13-tag taxonomy for each ticket. A hard cap of 5 in the schema prevents tag-spam.

### Why multi-label, not single-class

The dataset's native categorisation is multi-label (8 tag slots per ticket). After taxonomy trimming, true ground truth averages around 1.89 tags per ticket. Forcing single-class would lose information. Forcing always-N tags would introduce hallucinated padding.

### Why no hierarchical classification

An earlier version planned hierarchical type then queue prediction. The two fields are largely independent. Splitting into two stages doubled the LLM calls without reducing decision space. Single-call multi-label is cleaner, cheaper, and easier to evaluate.

### Why subject and body, not the answer field

Sample inspection of the dataset's `answer` column showed inconsistent content. Sometimes resolution text, sometimes clarifying questions to the customer, sometimes call-back offers. Not a reliable signal source. Subject and body only.

### LLM provider

Primary: Gemini 2.5 Flash. Fallback: Groq Llama 70B.

Driven by free tier availability, not raw price. Reference pricing per 1M tokens, input and output, as of April 2026:

| Provider, model | Input | Output | Free tier API |
| --- | --- | --- | --- |
| OpenAI GPT-5 Nano | $0.05 | $0.40 | No |
| Gemini 2.5 Flash-Lite | $0.10 | $0.40 | Yes |
| Gemini 2.5 Flash | $0.30 | $2.50 | Yes |
| Anthropic Claude Haiku 4.5 | $1.00 | $5.00 | No |

Google AI Studio gives 1500 requests per day free, which covers demo and most CI runs. Two-provider design (Gemini primary, Groq fallback) protects against single-provider outages and gives a real comparison surface.

### Prompt instruction

```text
Predict between 1 and 4 tags from the provided list.
Include only tags clearly supported by the ticket text.
Order by relevance, most relevant first.
```

### Pydantic schema

```python
class Tag(str, Enum):
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    DISRUPTION = "Disruption"
    CRASH = "Crash"
    NETWORK = "Network"
    DOCUMENTATION = "Documentation"
    FEATURE = "Feature"
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    PRODUCT = "Product"
    INTEGRATION = "Integration"
    MARKETING = "Marketing"
    SALES = "Sales"

class TicketClassification(BaseModel):
    tags: list[Tag] = Field(min_length=1, max_length=5)
    reasoning: str | None = None  # for debugging, not used in eval
```

---

## System architecture

```text
                    Internet (user)
                           │
                           ▼
              ┌────────────────────────┐
              │   Cloudflare (edge)    │
              │  TLS, DDoS, DNS        │
              └────────┬───────────────┘
                       │
                       ▼ (cloudflared tunnel, outbound)
         ┌─────────────────────────────────┐
         │     Mini PC (Windows + Docker)  │
         │                                 │
         │   ┌─────────────────────────┐   │
         │   │  cloudflared container  │   │
         │   │  routes:                │   │
         │   │   app.dom → :8501       │   │
         │   │   api.dom → :8000       │   │
         │   │   trace.dom → :3000     │   │
         │   └──────┬──────┬──────┬────┘   │
         │          │      │      │        │
         │     ┌────▼─┐ ┌─▼────┐ ┌▼──────┐ │
         │     │ UI   │ │ API  │ │Langfuse│ │
         │     │Strlit│ │FAPI  │ │  web   │ │
         │     │:8501 │ │:8000 │ │ :3000  │ │
         │     └──────┘ └──┬───┘ └───┬────┘ │
         │                 │         │      │
         │          ┌──────▼───┐ ┌──▼────┐  │
         │          │ Postgres │ │LF-pg  │  │
         │          │  main    │ │       │  │
         │          └──────────┘ └───────┘  │
         └─────────────────────────────────┘
                       │
                       ▼ (HTTPS, outbound)
              ┌────────────────────┐
              │  Google AI Studio  │
              │  (Gemini 2.5 Flash)│
              └────────────────────┘
```

### User flow

1. User opens `app.your-domain.com`, lands on the Streamlit UI through Cloudflare Tunnel.
2. Uploads a CSV of tickets.
3. Streamlit POSTs to FastAPI through the internal Docker network.
4. FastAPI validates the CSV, creates Job and Tickets in Postgres, returns job_id.
5. An async background poller picks up queued tickets and runs the classifier.
6. Each LLM call checks cache, retries with exponential backoff, validates tags against the enum.
7. Streamlit polls the job and shows a progress bar.
8. On completion, Pareto analysis runs and an Excel report is generated for download.
9. Each LLM call sends a trace to self-hosted Langfuse.

### Architectural decisions

| Decision | Rationale |
| --- | --- |
| FastAPI instead of Django | Standard in the AI ecosystem, native async, Pydantic built in |
| Streamlit instead of React | Backend-and-AI focus, but see iteration plan for UI replacement options |
| FastAPI BackgroundTasks plus Postgres queue, not Celery or Redis | At 1k to 10k tickets per job, Postgres is enough as a queue |
| No reverse proxy (Caddy or Nginx) | Cloudflare Tunnel routes subdomains, smaller config surface |
| Langfuse instead of Prometheus and Grafana | Observability of this system lives in the AI layer, not in HTTP overhead |
| SQLAlchemy 2.0 async | Aligned with FastAPI async flow |
| uv instead of pip or poetry | Fast package manager, current standard |
| Single-stage multi-label, not hierarchical | Type and queue are orthogonal in this dataset, two stages added cost without accuracy gain |
| Trimmed 13-tag taxonomy, not raw 20 tags | Manual review of 50 tickets found 56% had questionable tags. Trimmed taxonomy passes the noise floor |
| Mini PC, not Hetzner VPS | Existing infrastructure, no cost. Hetzner on iteration backlog if uptime becomes an issue |

---

## Tech stack

Backend:

- Python 3.12
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0 async plus Alembic
- tenacity for retry logic
- structlog for structured JSON logging

AI:

- Google Gemini 2.5 Flash, primary LLM
- Groq Llama 70B, fallback
- Google GenAI SDK (`google-genai`)
- Langfuse self-hosted for observability

Frontend:

- Streamlit, separate container

Data:

- PostgreSQL 16, main app
- PostgreSQL 16, separate instance for Langfuse
- HuggingFace `datasets` library for source data loading

Infrastructure:

- Docker plus Docker Compose v2
- Mini PC, Windows host with Docker Desktop
- Cloudflare Tunnel for public access and TLS
- GitHub Container Registry (GHCR)
- GitHub Actions for CI/CD
- UptimeRobot for uptime monitoring

Developer tooling:

- uv package manager
- ruff for lint and format
- mypy for type checking
- pytest plus pytest-asyncio
- pre-commit hooks

Export:

- openpyxl for Excel reports with charts

---

## Repository structure

```text
ticket-tag-classifier/
│
├── .github/
│   └── workflows/
│       ├── ci.yml                    # test + lint + eval
│       └── deploy.yml                # build + push + SSH deploy
│
├── apps/
│   ├── api/                          # FastAPI backend
│   │   ├── src/api/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   ├── ai/
│   │   │   │   ├── schemas.py        # Pydantic + TagEnum
│   │   │   │   ├── prompts.py        # MD loader
│   │   │   │   ├── classifier.py     # multi-label classifier
│   │   │   │   ├── cache.py          # Postgres-backed cache
│   │   │   │   └── prompts/
│   │   │   │       ├── v1_tags.md
│   │   │   │       └── v2_tags.md
│   │   │   ├── analysis/
│   │   │   │   ├── pareto.py
│   │   │   │   └── export.py         # Excel
│   │   │   ├── db/
│   │   │   │   ├── models.py         # SQLAlchemy
│   │   │   │   ├── session.py
│   │   │   │   └── migrations/
│   │   │   ├── routes/
│   │   │   │   ├── jobs.py
│   │   │   │   └── health.py
│   │   │   ├── workers/
│   │   │   │   └── poller.py         # async processing
│   │   │   └── observability/
│   │   │       └── langfuse.py
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   └── integration/
│   │   ├── alembic.ini
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   └── ui/                           # Streamlit frontend
│       ├── src/ui/
│       │   ├── main.py
│       │   ├── api_client.py
│       │   └── pages/
│       ├── Dockerfile
│       └── pyproject.toml
│
├── evals/
│   ├── ground_truth/
│   │   ├── v1.jsonl                  # versioned ground truth
│   │   ├── v2.jsonl
│   │   ├── adversarial.jsonl         # hard cases
│   │   ├── slices.yaml               # slicing definitions
│   │   └── CHANGELOG.md
│   ├── baselines/
│   │   ├── keyword_baseline.py       # dumb regex/keyword classifier
│   │   └── always_top_tags.py        # baseline that predicts top-N most frequent tags
│   ├── pareto_rubric/
│   │   ├── sample_csvs/              # 5 to 10 sample CSVs for qualitative report eval
│   │   ├── rubric.md                 # 3-item scoring rubric
│   │   └── reviews/                  # human review notes per generated report
│   ├── ci_thresholds.yaml            # calibrated per-tag floors
│   ├── run_eval.py
│   ├── compare_runs.py
│   ├── metrics.py
│   ├── reports/
│   └── README.md
│
├── data/
│   ├── taxonomy.yaml                 # versioned with eval
│   ├── load_dataset.py               # HuggingFace loader + filters
│   └── eda/
│       └── dataset_exploration.ipynb # week 3 EDA notebook
│
├── infra/
│   ├── docker-compose.yml            # dev
│   ├── docker-compose.prod.yml       # prod override
│   ├── .env.example
│   └── cloudflared/
│       └── config.example.yml
│
├── scripts/
│   ├── deploy.sh
│   └── seed_taxonomy.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── EVALS.md                      # full eval methodology
│   ├── TAXONOMY.md                   # tag definitions and edge cases
│   ├── DATASET.md                    # source, filters, label noise findings
│   ├── DEPLOYMENT.md
│   ├── PROMPT_VERSIONING.md
│   ├── STRUCTURE.md
│   └── images/
│
├── .pre-commit-config.yaml
├── .gitignore
├── .dockerignore
├── pyproject.toml
├── Makefile
├── LICENSE
└── README.md
```

---

## Evaluation methodology

Production-grade evaluation harness with versioned ground truth, multi-level metrics, and a CI gate calibrated against measured baselines.

### Ground truth dataset

Size: 500 tickets sampled from the filtered dataset.

Sourcing: stratified random sample, 30 to 40 per tag where possible, accepting class imbalance for tail tags. Native labels are trimmed to the 13-tag taxonomy. A 30-ticket spot check on the trimmed labels validates the noise rate.

Versioning: ground truth stored as `evals/ground_truth/vN.jsonl`, each version immutable once tagged. Changes to taxonomy or labels create a new version. `CHANGELOG.md` records what changed and why.

Format:

```json
{
  "ticket_id": 149,
  "subject": "Image Distortion on Projector Across Multiple Devices",
  "body": "Dear Customer Support Team,\n\nI am reaching out...",
  "type": "Incident",
  "queue": "Product Support",
  "priority": "low",
  "true_tags": ["Hardware", "Performance", "Disruption"],
  "sampled_at": "2026-05-22",
  "labelled_by": "ks",
  "labelled_at": null,
  "review_notes": null,
  "slice_tags": ["short", "low_priority"]
}
```

### Why no inter-annotator agreement

No second domain expert is available. Risk accepted. Mitigation: the 50-ticket preflight review (documented in `docs/DATASET.md`) was a pseudo inter-annotator pass, comparing my labels to AI-suggested labels with reasoning. Agreement rate of around 44% on the original taxonomy drove the trim to 13 tags. Intra-annotator self-consistency on 30 tickets at week 3 substitutes for the rest.

### Metrics

Every eval run produces:

#### Aggregate metrics

- Macro F1 across all 13 tags (averages each tag equally, surfaces tail tag failures)
- Micro F1 weighted by frequency (matches what production sees)
- Hamming loss
- Subset accuracy (exact match of predicted set to true set, reported but not gated)

#### Per-tag metrics

- Precision, recall, F1 per tag
- Per-tag confusion: which tags get swapped or missed

#### Slice metrics

- Accuracy on short tickets (under 200 chars)
- Accuracy on long tickets (over 600 chars)
- Accuracy on adversarial cases
- Accuracy by ticket priority field

#### Cost and performance

- Total cost USD per run
- Cost per ticket, average
- Latency p50, p95
- Cache hit rate

#### Pareto report quality (qualitative)

A 3-item rubric scored on 5 to 10 sample CSVs of around 200 tickets each:

- Top-3 tags in the report match what eyeball inspection of the data shows
- Ordering of categories is plausible
- Insights section says something non-generic

Score under 2 of 3 on any sample is flagged as a regression in the eval report.

### Baselines

Three baselines measured and recorded:

**Keyword baseline**: simple keyword matching classifier (`evals/baselines/keyword_baseline.py`). Establishes the floor below which the LLM is not adding value.

**Always-top-tags baseline**: predicts the 2 most frequent tags for every ticket. Reveals whether the model is doing better than naive frequency exploitation.

**Self-consistency check**: I label 30 tickets twice with a 3 to 4 day gap and measure intra-annotator agreement. Documented in `docs/EVALS.md` as the practical ceiling.

### CI gate policy

Per-tag F1 floors plus aggregate floors. A merge is blocked if any of:

- Macro F1 drops below `aggregate_macro_floor`
- Micro F1 drops below `aggregate_micro_floor`
- Any per-tag F1 drops below its `per_tag_floor` (set per tag based on baseline measurement and class size)
- Total cost per ticket increases by more than 50% over rolling baseline

Floors are calibrated after week 5, when the first end-to-end LLM run on full ground truth produces real numbers. Tighter floors on dominant tags (Performance, Disruption). Wider floors on tail tags (Marketing, Integration).

Tolerance below baseline reflects measurement noise. At n=500, standard error on per-tag F1 is around 2 to 4pp depending on class size. The default tolerance is the larger of 5pp or one standard error, not a flat 3pp.

```yaml
# evals/ci_thresholds.yaml
ground_truth_version: v1
calibrated_at: "2026-06-15"
calibrated_against:
  macro_f1: 0.72
  micro_f1: 0.81
  cost_per_ticket: 0.0012

floors:
  aggregate_macro_floor: 0.67
  aggregate_micro_floor: 0.76
  cost_increase_max: 1.5
  per_tag_floor:
    Security: 0.80
    Performance: 0.85       # dominant, tighter floor
    Disruption: 0.75
    Crash: 0.72
    Network: 0.70
    Documentation: 0.65
    Feature: 0.65
    Hardware: 0.60
    Software: 0.65
    Product: 0.55
    Integration: 0.55
    Marketing: 0.50         # tail, wider tolerance
    Sales: 0.50             # tail, wider tolerance
```

Floors revised whenever ground truth version changes or whenever a new prompt version stabilises a higher baseline (ratchet upward, not downward).

### Eval run modes

`python evals/run_eval.py --mode quick` runs on `adversarial.jsonl` only (around 50 examples), under 30 seconds, used during development.

`python evals/run_eval.py --mode full` runs on the entire ground truth, takes around 5 to 10 minutes, used in CI and before merging.

`python evals/run_eval.py --mode pareto-rubric` runs the pipeline on the 5 to 10 sample CSVs and prints generated reports for human review against the rubric. Manual scoring step, not automated.

`python evals/compare_runs.py --against main` runs the same dataset on the current branch and on main, produces a diff report.

### Adversarial test set

Separate file `evals/ground_truth/adversarial.jsonl`, around 30 to 50 examples, deliberately curated to be hard:

- Tickets with multiple plausibly valid tags
- Tickets with vague or short subjects
- Tickets where the trimmed taxonomy gives an awkward fit
- Edge cases discovered during development

Tracked separately so regressions on hard cases are visible even when aggregate F1 looks fine.

---

## Weekly plan, 12 weeks

### Phase 1: AI fundamentals and data, weeks 1 to 4

#### Week 1: Setup and first LLM call

Goals:

- Working repo with pre-commit hooks
- First FastAPI endpoint returning JSON
- First LLM call from Python returning structured output

Tasks:

- Create repo, `uv init`, directory structure
- Configure pre-commit (ruff, detect-secrets)
- Minimal FastAPI `main.py` with `/healthz`
- Set up Google AI Studio account, API key
- First LLM call: "Predict tags: Database is down" returning JSON list
- Pydantic model with TagEnum (13 tags from `docs/TAXONOMY.md`)

Learning, around 8h:

- Official FastAPI tutorial: First Steps, Path Parameters, Body, 4h
- Gemini Python SDK docs, Structured output section, 2h
- Pydantic v2: Models and Enums, 2h

Definition of done:

```bash
python -c "from api.ai.classifier import classify; print(classify('server down'))"
# {"tags": ["Disruption", "Crash"], "reasoning": "..."}
```

---

#### Week 2: Dataset loading

Most of the taxonomy work is done already (see `docs/TAXONOMY.md` and `docs/DATASET.md`). Week 2 focuses on building `load_dataset.py` correctly with all the filters.

Goals:

- `data/load_dataset.py` produces filtered, deduped, taxonomy-trimmed dataframe
- Final dataset size matches expectations (around 16,500 tickets)
- `data/taxonomy.yaml` valid and parseable by Pydantic enum

Tasks:

- Build `data/load_dataset.py`:
  - Loads Tobi-Bueck/customer-support-tickets via HuggingFace `datasets` library
  - Filter 1: language == 'en'
  - Filter 2: queue in pure-IT set
  - Filter 3: drop support-agent reply patterns (LIKE 'Thank you for contacting us%' etc.)
  - Filter 4: dedup on (subject, body) hash
  - Filter 5: trim tags to 13-tag taxonomy
  - Filter 6: drop tickets with zero kept tags
  - Returns pandas dataframe with columns: id, subject, body, type, queue, priority, tags (list)
  - Caches locally to `data/cache/` to avoid re-downloading
  - Logs ticket counts at each filter step
- Write `data/taxonomy.yaml` (machine-readable, used by classifier)
- Verify against expected counts: should land near 16,500 after all filters
- Update `docs/DATASET.md` with the actual final number after dedup

Learning, around 4h:

- HuggingFace `datasets` library basics
- pandas filtering on multiple conditions
- YAML basics

Definition of done:

```bash
python -c "from data.load_dataset import load; df = load(); print(df.shape)"
# (~16500, ~7)
```

---

#### Week 3: Ground truth, baselines, eval harness

Goals:

- 500 tickets sampled with trimmed-taxonomy labels
- Spot check on 30 tickets confirms noise rate after trim is acceptable (<15%)
- Keyword baseline running and measured
- Always-top-tags baseline running and measured
- Self-consistency baseline measured
- `evals/run_eval.py` produces structured report
- Adversarial subset identified
- EDA notebook with distribution analysis

Tasks:

- Stratified sample 500 tickets from filtered dataset
- Build `data/eda/dataset_exploration.ipynb`:
  - Per-tag frequency in filtered dataset
  - Body length distribution per tag
  - Tag co-occurrence matrix
  - Class imbalance visualisation
- Spot check 30 random tickets from the sampled 500. Verify trimmed labels still fit. Compute noise rate and document in `docs/DATASET.md`
- Self-consistency: re-label 30 of them after a 3 to 4 day gap, compute agreement
- Build `evals/baselines/keyword_baseline.py`
- Build `evals/baselines/always_top_tags.py`
- Run both baselines on ground truth, record numbers in `docs/EVALS.md`
- Build `evals/run_eval.py`:
  - Load ground truth version, run classifier (or baseline), compute metrics
  - Output JSON report to `evals/reports/{timestamp}.json`
  - Output Markdown summary
- Build `evals/metrics.py`:
  - Macro F1, micro F1, Hamming loss, subset accuracy
  - Per-tag precision/recall/F1
  - Per-tag confusion patterns
  - Slice computations (length, priority)
- Curate `adversarial.jsonl`: 30 to 50 hard tickets
- Tag ground truth as v1, write `CHANGELOG.md`

Learning, around 4h:

- scikit-learn metrics (multi-label specific)
- JSON Lines format
- pandas plotting and seaborn

Definition of done:

```bash
wc -l evals/ground_truth/v1.jsonl
# 500

python evals/run_eval.py --classifier keyword --gt v1
# Macro F1: 0.41, Micro F1: 0.55

# Self-consistency documented in docs/EVALS.md
```

---

#### Week 4: Postgres, SQLAlchemy, basic jobs flow

Goals:

- `make dev` brings up docker-compose with Postgres
- POST /jobs accepts CSV and creates Job in DB
- GET /jobs/{id} returns status

Tasks:

- `docker-compose.yml`: api service plus postgres service
- SQLAlchemy models: Job, Ticket, Classification, LLMCall
- Alembic setup plus first migration
- Route POST /jobs with UploadFile
- Route GET /jobs/{id}
- Startup event: test DB connection
- Async SQLAlchemy sessions

Learning, around 8h, heavy week:

- SQLAlchemy 2.0 tutorial, 4 to 5h
- Alembic quickstart, 1h
- FastAPI async dependencies, 2h
- Docker compose networks, 1h

Definition of done:

- `curl -F file=@test.csv http://localhost:8000/jobs` returns `{"job_id": "..."}`
- `curl http://localhost:8000/jobs/{id}` returns status
- Data visible in psql

---

### Phase 2: Backend core and classifier, weeks 5 to 7

#### Week 5: Classifier in pipeline, cache, retry, calibration

Goals:

- A created job is processed (sync to start, async in week 6)
- Each ticket runs through the multi-label classifier
- Results cached at hash(content + prompt) level
- Retry with backoff on errors
- First measured LLM accuracy on full ground truth, used to calibrate CI thresholds

Tasks:

- Build classifier:
  - Load prompt from `prompts/v1_tags.md`
  - Call Gemini 2.5 Flash with structured output (TagEnum list)
  - Validate response against Pydantic schema
  - Fallback to Groq Llama 70B on Gemini error
- Integrate classifier with DB pipeline (week 4)
- Table `llm_calls` with: hash, prompt_version, response, tokens_in, tokens_out, cost_usd, latency_ms
- Cache check before each LLM call
- tenacity retry: exponential backoff, max 3 attempts
- Fallback to empty tag list with "uncategorized" flag on persistent failure
- Validation: enforce all returned tags are in the enum, retry with extra instruction if hallucination occurs
- Run full eval on ground truth v1, record baseline numbers
- Calibrate CI thresholds:
  - Per-tag floors set to baseline F1 minus larger of 5pp or one standard error
  - Aggregate floors set to baseline minus 5pp
  - Document calibration in `evals/ci_thresholds.yaml` with timestamp and rationale
- Write `docs/EVALS.md`: methodology, baselines, calibration approach

Learning, around 3h:

- tenacity basics
- hashlib plus canonical JSON for cache keys

Definition of done:

- Send 50 tickets, all get tag predictions
- Re-run on same CSV is 100x faster from cache hits
- DB shows `llm_calls` with costs
- `evals/ci_thresholds.yaml` populated with measured-baseline floors
- Full eval report in `evals/reports/`

---

#### Week 6: Async poller plus Langfuse

Goals:

- Job processing in the background, no request blocking
- Langfuse shows traces, costs, latencies
- Minimal UI shows progress

Tasks:

- Async poller as a background task on FastAPI startup (`asyncio.create_task`)
- Loop: pull queued tickets (LIMIT 10), process batch, update `job.progress`
- docker-compose adds `langfuse-web` plus `langfuse-postgres`
- Langfuse SDK in classifier: `@observe` decorator
- Trace structure: per-ticket span with token usage and cost
- Screenshot dashboard into `docs/images/`

Learning, around 4h:

- Langfuse self-hosted setup, 2h
- asyncio tasks and lifecycle, 2h

Definition of done:

- Upload CSV, see each LLM call in Langfuse with cost and latency
- Cost per job visible in Langfuse dashboard
- Streamlit shows progress bar (poll GET /jobs/{id})

---

#### Week 7: Streamlit UI, full flow

Goals:

- User completes the whole app without touching the API directly
- Sensible UX (errors, empty states)

Tasks:

- `apps/ui/` separate project with pyproject
- Sidebar nav plus pages: upload, results, evals
- Upload: `st.file_uploader` plus POST to api:8000/jobs
- Progress: `st.spinner` plus polling GET /jobs/{id}
- Results: `st.dataframe` with filters, tags shown as chips
- Download Excel button
- Error handling: API down, malformed CSV
- Eval page: load latest report, show macro/micro F1, per-tag breakdown
- Theme Streamlit (custom CSS, hide default menu) to look less like a default Streamlit app

Learning, around 5h:

- Streamlit docs, 3 to 4h
- `st.session_state`, 1h

Definition of done:

- Full user journey from upload to download without hitting the API directly
- Eval results visible in UI

Note: Streamlit has perception costs for recruiters. If schedule allows or motivation is high, consider replacing with a single static HTML page that calls the FastAPI directly. Logged in iteration plan.

---

### Phase 3: Reporting and deployment, weeks 8 to 11

#### Week 8: Pareto analysis, Excel export, Pareto rubric eval

Goals:

- After job completion, generate a Pareto report
- Excel with charts to download
- Pareto report quality measured against rubric on sample CSVs

Tasks:

- `analysis/pareto.py`: top-N tags by frequency, with co-occurrence breakdowns
- `analysis/export.py`: openpyxl with 5 sheets:
  1. Raw data, all tickets plus predicted tags
  2. Pareto table at tag level
  3. Tag co-occurrence table
  4. Pareto chart, bar plus line
  5. Insights section with top 3 tags, trends, anomalies
- UI: "Insights" section
- Pareto rubric eval:
  - Build 5 to 10 sample CSVs of 200 tickets each from filtered dataset
  - Generate report for each
  - Score each against the 3-item rubric
  - Document scores in `evals/pareto_rubric/reviews/`
- Update `evals/ci_thresholds.yaml` with the rubric pass criterion (e.g., median score >= 2 of 3)

Learning, around 3h:

- openpyxl charts, 2h
- Pareto algorithm, 30 min

Definition of done:

- Excel download produces a file that looks like a real report
- Rubric scores recorded for at least 5 sample CSVs

---

#### Week 9: Production deployment from mini PC

Goals:

- App is live on a public domain via mini PC
- Deploy a new version manually with one command

Tasks:

- Mini PC setup audit:
  - Docker Desktop running
  - Cloudflare Tunnel installed and authenticated
  - Auto-restart configured for Docker containers
- Cloudflare config: add the domain (buy if needed), create tunnel
- cloudflared config.yml with subdomain routing (app, api, trace)
- DNS records in Cloudflare (app, api, trace)
- `docker-compose.prod.yml`: GHCR tags, restart policies
- `docker compose up -d`, test public access
- Backup strategy: Postgres dump to external drive nightly, kept for 7 days
- UptimeRobot monitor on app.your-domain.com

Learning, around 4h:

- Cloudflare Tunnel docs, 2h
- docker compose overrides, 1h
- Windows Docker Desktop quirks, 1h

Definition of done:

- Click `https://app.your-domain.com`, see the app
- Mini PC reboots and the stack comes back automatically

---

#### Week 10: CI with eval gate

Goals:

- Every PR runs tests, lint, full eval
- Merge blocked if per-tag floor or aggregate floor violated
- Comparison report posted as PR comment

Tasks:

- `.github/workflows/ci.yml`:
  - Matrix: ubuntu-latest, python 3.12
  - Steps: checkout, setup uv, install, ruff, mypy, pytest
  - Eval step: run `evals/run_eval.py --mode full`
  - Compare against `ci_thresholds.yaml`, exit code 1 if violated
  - Post-run: GitHub Action that comments on PR with metric diff vs main
  - Cache uv deps and Gemini responses (cache shared across CI runs)
- Tests:
  - Unit: test_pareto, test_cache, test_schemas, test_taxonomy_validation
  - Integration: test_jobs_flow with testcontainers or SQLite in-memory
  - Eval-specific tests: test_metrics calculations, test_threshold_enforcement
- Branch protection on main: PR required, CI must pass

Learning, around 8h:

- GitHub Actions basics, 3h
- pytest plus pytest-asyncio, 2h
- pytest fixtures for DB, 2h
- GitHub Actions PR comment automation, 1h

Definition of done:

- Open a PR, see eval comparison comment with per-tag breakdown
- Merge blocked when per-tag F1 drops below floor
- Eval cost on CI run under $0.20 per PR

---

#### Week 11: CD, auto-deploy

Goals:

- Merge to main triggers production deploy within 2 minutes
- Rollback through revert commit

Tasks:

- `.github/workflows/deploy.yml`: trigger on push to main
- Steps:
  1. Build images (api, ui) tagged `sha-XXXX` plus `latest`
  2. Push to GHCR
  3. SSH to mini PC (or webhook trigger from mini PC pulling), `docker compose pull && docker compose up -d`
  4. Post-deploy healthcheck (curl /healthz)
  5. Optional Discord webhook notification
- GitHub Secrets: `SSH_PRIVATE_KEY` or webhook secret, `GHCR_TOKEN`
- `docs/DEPLOYMENT.md`

Note: SSH to a residential connection from GitHub Actions may have firewall issues. Fallback: webhook-based pull where the mini PC polls GHCR every minute and pulls when a new tag exists.

Learning, around 3h:

- GitHub Actions secrets plus SSH action
- GHCR permissions

Definition of done:

- Commit to main, around 90 seconds, production updated

---

### Phase 4: Polish, week 12

#### Week 12: Documentation, demo, write-up

Goals:

- The project looks like a finished product
- Everything ready to share

Tasks:

- `README.md`:
  - Hero section (what it is, why)
  - Synthetic data disclaimer with production-readiness section
  - Screenshots (UI, Langfuse dashboard, eval report, Excel output)
  - Architecture diagram (Mermaid)
  - Tech stack with one-line rationales
  - Quickstart
  - Link to live demo
- `docs/ARCHITECTURE.md`: decisions and trade-offs
- `docs/EVALS.md`: methodology, baselines, threshold calibration
- `docs/TAXONOMY.md`: tag definitions, edge cases, design rationale (already drafted)
- `docs/DATASET.md`: source, filters, label noise findings (already drafted)
- `docs/DEPLOYMENT.md`: mini PC setup step-by-step
- Demo video, 2 to 3 min (OBS Studio):
  - Upload CSV
  - Processing with Langfuse in the background
  - Results plus Excel download
  - Speedup from cache
  - Eval report walkthrough
- Write-up post: 300 to 500 words, what I built, what I learned, link

---

## What I deliberately do not build

| Skipped | Why |
| --- | --- |
| Kubernetes | Overkill for 6 containers on one host, plus 2 weeks with no demo value |
| Prometheus plus Grafana | Observability of this project lives in the AI layer (Langfuse), not HTTP |
| Redis plus RQ or Celery | Postgres as a queue is enough at this volume |
| Caddy or Nginx reverse proxy | Cloudflare Tunnel routes subdomains natively |
| Terraform | No cloud resources that justify IaC |
| Custom auth system | Cloudflare Access with OTP if needed |
| RAG, agents, fine-tuning | Tag classification needs none of these |
| Helm, ArgoCD, GitOps | No K8s, so no place for these tools |
| Service mesh (Istio, Linkerd) | 6 containers on one host, no traffic to manage |
| Kafka or RabbitMQ | No event-driven architecture |
| 80% test coverage target | Tests on the critical path, not for the metric |
| Inter-annotator agreement with second expert | Not available, intra-annotator self-consistency substitutes |
| Custom taxonomy | Trimmed dataset taxonomy keeps reasoning honest and reproducible |
| Bilingual (DE) support | German body labels would require ground truth verification I cannot do well |
| Hierarchical classification | Type and queue are orthogonal in this dataset, single-stage is cleaner |
| Tail-tag predictions (Elasticsearch, RAID-Controller, etc.) | Below the long-tail cutoff, taxonomy stays at 13 tags |
| Real-data validation pipeline | Client policy prevents access |
| Hetzner VPS | Mini PC works for current uptime needs, on iteration plan |

---

## Monthly budget

| Item | Cost (USD) | Notes |
| --- | --- | --- |
| Mini PC electricity | ~2 | Existing hardware |
| Gemini API | 0 to 3 | Free tier (1500 req/day) covers demo and most CI runs |
| Domain | ~0.83 | 10/year divided by 12 |
| Cloudflare | 0 | Free plan |
| GitHub Actions | 0 | Public repo, unlimited |
| GHCR | 0 | Public images, unlimited |
| UptimeRobot | 0 | Free, 50 monitors |
| HuggingFace dataset | 0 | Public dataset, CC BY-NC 4.0, free download |
| Total | ~3 to 6 USD/month | |

CI eval runs: at 500 ground truth examples and 1 LLM call per ticket, a full eval is 500 LLM calls. At Gemini Flash pricing this is roughly $0.05 per CI run. With caching, repeat runs on unchanged code are near-zero. Free tier limit (1500/day) supports up to 3 full evals per day plus development calls.

---

## Risks and contingencies

| Risk | Mitigation |
| --- | --- |
| Synthetic distribution differs from real production data | Explicit README disclaimer, pipeline designed data-source-agnostic so retraining on real data is configuration-only |
| Dataset license CC BY-NC 4.0 (non-commercial) | Portfolio use is non-commercial, full citation in README and DATASET.md |
| Native labels in source dataset contain errors | Manual review of 50 tickets confirmed 56% per-ticket noise rate. Trimmed taxonomy and filters address it. Documented in DATASET.md |
| Stuck on async SQLAlchemy (week 4) | Fallback to sync SQLAlchemy, minimal value loss |
| Langfuse self-host fails to start | Fallback to Langfuse Cloud free tier (50k observations/month) |
| Gemini free tier exhausted | Add card to Google AI Studio, costs 1 to 3 USD/month |
| LLM macro F1 below useful baseline (under 0.55) | Prompt iteration, consider including priority field as feature, review per-tag failures for taxonomy issues |
| Stuck on Streamlit UX | Accept minimal UI, focus on backend |
| Mini PC dies right before a demo | UptimeRobot alert plus rollback to previous SHA tag, fallback to Hetzner CX22 setup (2 days work) |
| Ground truth review takes longer than expected | Reduce sample size to 300 for v1, expand to v2 in week 8 |
| Residual noise in trimmed taxonomy still high (>20% after week 3 spot check) | Drop one or two more low-frequency tags, document in CHANGELOG |

---

## Iteration plan after completion

After week 12 the project is alive. Phase 2 backlog over the next 2 to 4 months. Each item is a separate write-up plus README update.

- Ground truth expansion to 1000+ examples
- A/B testing prompts with Langfuse datasets
- Switch primary model to Gemini 2.5 Flash-Lite where accuracy holds, cut LLM cost roughly 5x
- Adversarial set expansion through production data sampling
- UI replacement: single static HTML page calling FastAPI directly, drop Streamlit.
- Hetzner VPS migration if mini PC uptime becomes an issue
- Tighter queue filter: drop Product Support to remove residual sales/marketing tickets, measure impact
- Prometheus plus Grafana, if HTTP-layer observability becomes useful
- Fine-tuning a small model on collected ground truth
- Human-in-the-loop UI (user corrections feed back into ground truth v3, v4)
- Drift detection: alert when production ticket distribution diverges from ground truth distribution
