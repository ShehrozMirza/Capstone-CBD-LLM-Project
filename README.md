# Amazon Apparel → Customer Profiles → Year-Long Deal Campaign

Graduate capstone pipeline. Turns a millions-of-records Amazon apparel JSON
corpus into (a) cleaned product intelligence, (b) **12 distinct named customer
profiles**, and (c) a **52-week deal campaign per profile** with conversion
estimates and an **annual customer value (CLV proxy)**.

Runs locally on a normal laptop (8–16 GB RAM). The runnable codebase makes
**zero LLM/API calls** and is deterministic. LLMs are used only for two offline,
aggregate-only steps (brand standardization, profile naming), with prompts +
outputs saved as artifacts.

---

## Quick start

```bash
pip install -r requirements.txt

# Option A — smoke test the whole thing on synthetic data (no download):
make smoke

# Option B — real run:
python scripts/download_data.py --folder <GOOGLE_DRIVE_FOLDER_URL>   # -> data/raw/
make all                                                            # -> data/processed/
```

`make all` runs: `brandmap → ingest → normalize → intel → segment → campaign → value`.
Final results land in `data/processed/valuation_summary.csv`.

---

## Architecture (raw JSON in, intelligence out)

| Stage | File | What it does | Scales because |
|------|------|--------------|----------------|
| 0 | `scripts/make_brand_map.py` | Flattens the legacy R brand rules → `brand_map.json` (1,318 variants → 376 brands) | run-once, O(1) lookups at run time |
| 1 | `src/stage01_ingest.py` | Stream-parses corpus in 50k batches → parquet shards + product↔product **edge list** | fixed batch size, never loads corpus into RAM |
| 2 | `src/stage02_normalize.py` | Taxonomy assignment + brand standardization + price tier → "universal elements" | processes one shard at a time |
| 3 | `src/stage03_intelligence.py` | DuckDB out-of-core: brand stats, **brand↔brand co-occurrence**, category co-occurrence, graph centrality | DuckDB streams off parquet, larger-than-RAM safe |
| 4 | `src/stage04_segment.py` | Feature build + KMeans → 12 clusters → **fingerprints** for the LLM | clusters a representative sample, assigns rest by centroid |
| — | *LLM step 1* | Name the 12 profiles from `profile_fingerprints.json` | offline, aggregate only |
| 5 | `src/stage05_campaign.py` | 52 weekly deals + co-purchase bundles per profile, from **held-out** items | affinity-zone filtered, per-profile |
| 6 | `src/stage06_valuation.py` | Defended conversion model → expected annual orders → **CLV** | vectorized per profile |

### Key design decisions
- **Two-signal relationships.** `BOUGHT_WITH1` ("also bought", weight 1.0) is the
  backbone; `BOUGHT_WITH2` ("considered/liked", weight 0.35) is used but down-weighted.
- **Discovery / holdout split** (70/30) by deterministic hash of `retailerProductId`.
  Profiles are *discovered* on one split; deals are *operated* on the other.
- **Real-brand floor.** Brands with < 100 items are treated as long-tail noise and
  dropped from brand intelligence (~80k raw strings → a few thousand real brands).
- **Cadence ≠ frequency.** 52 weekly *offers* but a customer buys a *handful* of
  times/year. `stage06` caps expected annual orders well below 52 and applies
  offer-fatigue decay + seasonality.

---

## The LLM steps (the only place data touches a model)

Both are **offline, run-once, aggregate-only** — never the raw corpus.

1. **Brand standardization** — `llm/prompts/brand_standardization_prompt.md`.
   Feed the model a brand list with counts (not records); save its JSON to
   `llm/outputs/brand_overrides.json`; re-run `make brandmap` to bake it into
   `brand_map.json`. The pipeline then stays a pure dict lookup.
2. **Profile synthesis** — `llm/prompts/profile_synthesis_prompt.md`.
   Feed the 12 fingerprints from `stage04`; save to `profiles/profiles.json`;
   run `scripts/render_profile_cards.py` for human-readable cards.

Keep the exact prompt + raw model output in `llm/outputs/` for reproducibility.
A reviewer can re-run every deterministic stage with no tokens.

---

## Repository layout

```
amazon-apparel-capstone/
├── README.md  Makefile  requirements.txt  config.yaml  .gitignore
├── data/
│   ├── raw/         # corpus (gitignored)
│   ├── interim/     # parquet shards: products/, edges/, universal/ (gitignored)
│   ├── processed/   # brand_stats, cooccurrence, clusters, campaign, valuation
│   └── reference/   # taxonomy.py, brand_dicitonary.txt (R), brand_map.json
├── src/
│   ├── config.py  taxonomy_assign.py  brand_resolve.py  seasonality.py
│   └── stage01_ingest … stage06_valuation.py
├── scripts/
│   ├── make_brand_map.py  download_data.py  make_synthetic_corpus.py
│   └── render_profile_cards.py
├── llm/
│   ├── prompts/   # the two prompt templates
│   ├── inputs/    # aggregates handed to the LLM (profile_fingerprints.json)
│   └── outputs/   # saved model responses (reproducibility)
├── profiles/      # profiles.json + cards/*.md (the 12 personas)
├── campaign/      # per-profile campaign exports (optional)
├── tests/         # pytest sanity checks
└── presentation/  # slide outline
```

---

## Outputs you hand in
- `data/processed/brand_stats.parquet`, `brand_cooccurrence.parquet`, `brand_graph_metrics.parquet`
- `data/processed/product_clusters.parquet`, `llm/inputs/profile_fingerprints.json`
- `profiles/profiles.json` + `profiles/cards/*.md` (the 12 named profiles)
- `data/processed/campaign.parquet` (12 × 52 deals + bundles)
- `data/processed/valuation_summary.csv` + `conversion_cluster_XX.parquet`
- `llm/outputs/*` (prompts + responses)
- `presentation/` slides

## Limitations (be honest in the deck)
- No transaction log → conversion is a *modeled, defended* estimate, not measured.
- KMeans forces exactly 12 clusters; HDBSCAN would let cluster count emerge.
- Holdout centroid-assignment for non-sampled products is stubbed (see stage04 TODO).
- Seasonality/margin/frequency priors are assumptions in `config.yaml`, tunable.
```
