# Project Directory Tree

```text
pareto-tagger/
|
+-- .github/
|   +-- workflows/
|       +-- ci.yml                         # test + lint + eval gate
|       +-- deploy.yml                     # build + push + SSH deploy
|
+-- apps/
|   +-- api/                               # FastAPI backend
|   |   +-- src/api/
|   |   |   +-- main.py                    # app entrypoint
|   |   |   +-- config.py                  # settings from env
|   |   |   +-- logging.py                 # structlog setup
|   |   |   +-- ai/
|   |   |   |   +-- schemas.py             # Pydantic models + TagEnum
|   |   |   |   +-- prompts.py             # markdown prompt loader
|   |   |   |   +-- classifier.py          # multi-label classifier
|   |   |   |   +-- cache.py               # Postgres-backed cache
|   |   |   |   +-- prompts/
|   |   |   |       +-- v1_tags.md         # prompt version 1
|   |   |   |       +-- v2_tags.md         # prompt version 2
|   |   |   +-- analysis/
|   |   |   |   +-- pareto.py              # Pareto analysis logic
|   |   |   |   +-- export.py              # Excel report generation
|   |   |   +-- db/
|   |   |   |   +-- models.py              # SQLAlchemy models
|   |   |   |   +-- session.py             # async session factory
|   |   |   |   +-- migrations/            # Alembic migrations
|   |   |   +-- routes/
|   |   |   |   +-- jobs.py                # POST /jobs, GET /jobs/{id}
|   |   |   |   +-- health.py              # GET /healthz
|   |   |   +-- workers/
|   |   |   |   +-- poller.py              # async background processor
|   |   |   +-- observability/
|   |   |       +-- langfuse.py            # Langfuse SDK integration
|   |   +-- tests/
|   |   |   +-- unit/                      # pure logic tests
|   |   |   +-- integration/               # DB + API flow tests
|   |   +-- alembic.ini
|   |   +-- Dockerfile
|   |   +-- pyproject.toml
|   |
|   +-- ui/                                # Streamlit frontend
|       +-- src/ui/
|       |   +-- main.py                    # Streamlit entrypoint
|       |   +-- api_client.py              # HTTP client for FastAPI
|       |   +-- pages/                     # upload, results, evals
|       +-- Dockerfile
|       +-- pyproject.toml
|
+-- evals/
|   +-- ground_truth/
|   |   +-- v1.jsonl                       # ground truth v1, immutable once tagged
|   |   +-- v2.jsonl                       # ground truth v2
|   |   +-- adversarial.jsonl              # hard edge cases, 30-50 tickets
|   |   +-- slices.yaml                    # slice definitions
|   |   +-- CHANGELOG.md                   # what changed and why
|   +-- baselines/
|   |   +-- keyword_baseline.py            # regex/keyword classifier floor
|   |   +-- always_top_tags.py             # predict top-N most frequent tags
|   +-- pareto_rubric/
|   |   +-- sample_csvs/                   # 5-10 sample CSVs of ~200 tickets
|   |   +-- rubric.md                      # 3-item scoring rubric
|   |   +-- reviews/                       # human review notes per report
|   +-- ci_thresholds.yaml                 # per-tag F1 floors, calibrated week 5
|   +-- run_eval.py                        # eval runner: quick / full / pareto-rubric
|   +-- compare_runs.py                    # diff two eval runs
|   +-- metrics.py                         # F1, Hamming loss, per-tag, slices
|   +-- reports/                           # timestamped JSON + Markdown outputs
|   +-- README.md
|
+-- data/
|   +-- taxonomy.yaml                      # machine-readable taxonomy
|   +-- load_dataset.py                    # HuggingFace loader + all 6 filters
|   +-- cache/                             # local dataset cache, gitignored
|   +-- eda/
|       +-- dataset_exploration.ipynb      # week 3 EDA notebook
|
+-- infra/
|   +-- docker-compose.yml                 # dev stack
|   +-- docker-compose.prod.yml            # prod overrides
|   +-- .env.example                       # env var template
|   +-- cloudflared/
|       +-- config.example.yml             # Cloudflare Tunnel routing
|
+-- scripts/
|   +-- deploy.sh                          # manual deploy helper
|   +-- seed_taxonomy.py                   # seed taxonomy.yaml into DB
|
+-- docs/
|   +-- ARCHITECTURE.md                    # decisions and trade-offs
|   +-- EVALS.md                           # eval methodology, baselines, calibration
|   +-- TAXONOMY.md                        # tag definitions, edge cases, rationale
|   +-- DATASET.md                         # source, filters, label noise findings
|   +-- DEPLOYMENT.md                      # mini PC setup step-by-step
|   +-- PROMPT_VERSIONING.md               # prompt change log and versioning rules
|   +-- STRUCTURE.md                       # this file
|   +-- images/                            # screenshots for README and docs
|
+-- .pre-commit-config.yaml                # ruff, detect-secrets
+-- .gitignore
+-- .dockerignore
+-- .python-version
+-- pyproject.toml                         # root-level uv workspace config
+-- Makefile                               # make dev, make test, make eval
+-- LICENSE
+-- README.md
```

## Key rules

- apps/api and apps/ui are separate uv projects with their own pyproject.toml
- Root pyproject.toml is the uv workspace config only
- data/cache/ is gitignored, dataset downloads at runtime
- evals/ground_truth/vN.jsonl is immutable once tagged, changes create a new version
- evals/ci_thresholds.yaml is calibrated after week 5 when first real LLM baseline is measured
- .gitkeep files hold empty directories until real files land
