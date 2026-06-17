# Amazon Apparel → Customer Profiles → Year-Long Deal Campaign

> Graduate capstone pipeline that turns a millions-of-records Amazon apparel JSON corpus into **12 distinct named customer profiles** and a **52-week deal campaign per profile** with conversion estimates and an **annual customer value (CLV proxy)**.

Runs locally on a normal laptop (8–16 GB RAM). The runnable codebase makes **zero LLM/API calls** and is fully deterministic. LLMs are used only for two offline, aggregate-only steps (brand standardization, profile naming), with prompts + outputs saved as artifacts.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Pipeline Overview](#pipeline-overview)
- [Detailed Flow Diagrams](#detailed-flow-diagrams)
  - [Stage 1 – Ingest](#stage-1--ingest)
  - [Stage 3 – Intelligence (Brand Graph)](#stage-3--intelligence-brand-graph)
  - [Stage 4 – Segmentation](#stage-4--segmentation)
  - [Stage 5 – Campaign Generation](#stage-5--campaign-generation)
  - [Stage 6 – Valuation (CLV Model)](#stage-6--valuation-clv-model)
  - [LLM Integration Points](#llm-integration-points)
- [Presentation](#presentation)
- [Repository Layout](#repository-layout)
- [Key Design Decisions](#key-design-decisions)
- [Outputs](#outputs)
- [Limitations](#limitations)

---

## Quick Start

```bash
pip install -r requirements.txt

# Option A — smoke test the whole pipeline on synthetic data (no download needed):
make smoke

# Option B — real run (requires the corpus):
python scripts/download_data.py --folder <GOOGLE_DRIVE_FOLDER_URL>   # -> data/raw/
make all                                                              # -> data/processed/
```

`make all` runs: `brandmap → ingest → normalize → intel → segment → campaign → value`

Final results land in `data/processed/valuation_summary.csv`.

---

## Pipeline Overview

```mermaid
flowchart TD
    A[("🗂️ Raw Amazon\nApparel JSON\nCorpus")] --> B

    subgraph DETERMINISTIC ["⚙️ Deterministic Pipeline (make all)"]
        B["Stage 0\nBrand Map\nmake_brand_map.py\n1,318 variants → 376 brands"]
        B --> C["Stage 1 – Ingest\nstage01_ingest.py\nStream 50k-record batches\n→ Parquet shards + edge list"]
        C --> D["Stage 2 – Normalize\nstage02_normalize.py\nTaxonomy + brand resolve\n+ price tier"]
        D --> E["Stage 3 – Intelligence\nstage03_intelligence.py\nDuckDB: brand stats,\nco-occurrence, graph centrality"]
        E --> F["Stage 4 – Segment\nstage04_segment.py\nKMeans → 12 clusters\n→ Profile fingerprints"]
    end

    F --> G[/"llm/inputs/\nprofile_fingerprints.json"/]
    G --> H[["🤖 LLM Step 2\nProfile Synthesis\n(offline, run-once)\nnames 12 personas"]]
    H --> I[/"profiles/\nprofiles.json"/]

    subgraph DETERMINISTIC2 ["⚙️ Deterministic Pipeline (continued)"]
        I --> J["Stage 5 – Campaign\nstage05_campaign.py\n52 weekly deals per profile\nfrom holdout items"]
        J --> K["Stage 6 – Valuation\nstage06_valuation.py\nConversion model\n→ CLV per profile"]
    end

    K --> L[("📊 valuation_summary.csv\n12 profiles × annual value")]

    style DETERMINISTIC fill:#e8f4f8,stroke:#2196F3,stroke-width:2px
    style DETERMINISTIC2 fill:#e8f4f8,stroke:#2196F3,stroke-width:2px
    style H fill:#fff3cd,stroke:#ff9800,stroke-width:2px
```

---

## Detailed Flow Diagrams

### Stage 1 – Ingest

```mermaid
flowchart TD
    A[Raw Directory\ndata/raw/] --> B{Layout\nDetection}
    B -->|"*.jsonl shards"| C[Line-stream\nJSON parser]
    B -->|"nested *.json files"| D[Glob file\niterator]
    C --> E[Record\nValidator]
    D --> E
    E -->|"missing pid\nor short title"| F[🗑️ Drop]
    E -->|valid| G[Flatten Record\nto Row Dict]
    G --> H["Hash(pid + seed)\n→ discovery / holdout\n(70 / 30 split)"]
    H --> I[Extract\nBOUGHT_WITH1\nBOUGHT_WITH2\nedges]
    G --> J[Product\nBuffer]
    I --> K[Edge\nBuffer]
    J & K --> L{Buffer\nfull?\n50k rows}
    L -->|yes| M[Flush to Parquet\ndata/interim/products/\ndata/interim/edges/]
    L -->|no| G
    M --> N[GC Collect\n+ next shard]
```

### Stage 2 – Normalize

```mermaid
flowchart TD
    A[/"data/interim/products/\n*.parquet shards"/] --> B
    C[/"data/reference/\nbrand_map.json"/] --> D["BrandResolver\nO(1) dict lookup"]

    B["Load one shard\nat a time"]
    B --> E["assign_category\ntitle + desc + hierarchy\n→ category + klass"]
    B --> D
    D --> F["Resolved brand\n(canonical name)"]
    B --> G["price_tier\n< $25 → value\n$25–$75 → mid\n> $75 → premium"]

    E --> H["Merge columns\npid, brand, category, klass\ngender, color, retail_price\nprice_tier, n_sizes, split, title"]
    F --> H
    G --> H

    H --> I[/"data/interim/universal/\npart-XXXXX.parquet\n(universal elements)"/]
    I --> J[Next shard]
```

### Stage 3 – Intelligence (Brand Graph)

```mermaid
flowchart LR
    A[/"data/interim/\nuniversal/*.parquet"/] --> B
    C[/"data/interim/\nedges/*.parquet"/] --> B

    B["DuckDB\n(out-of-core,\nlarger-than-RAM safe)"]

    B --> D["brand_stats\nitem count, categories,\nprice tier, 'real' flag\n(≥ 100 items)"]
    B --> E["brand_cooccurrence\nweighted brand↔brand edges\nBW1×1.0 + BW2×0.35\n(min 3 co-purchases)"]
    B --> F["category_cooccurrence\nklass↔klass cross-sell\nsignal"]

    E --> G["igraph\nGraph Centrality"]
    G --> H["brand_graph_metrics\ndegree, weighted degree\neigen-centrality\nbetweenness"]

    D --> I[/"data/processed/\nbrand_stats.parquet"/]
    E --> J[/"data/processed/\nbrand_cooccurrence.parquet"/]
    H --> K[/"data/processed/\nbrand_graph_metrics.parquet"/]
```

### Stage 4 – Segmentation

```mermaid
flowchart TD
    A[/"data/interim/universal/\n*.parquet  (discovery split)"/] --> B
    C[/"data/processed/\nbrand_graph_metrics.parquet"/] --> B

    B["DuckDB sample\n300k products"]
    B --> D["Feature Matrix\ncategory OHE\nprice tier OHE\ngender OHE\nretail_price\nbrand eigen / wdeg"]
    D --> E["StandardScaler\nnormalize features"]
    E --> F["KMeans\nn=12, n_init=10\nrandom_state=42"]
    F --> G["12 Clusters"]
    G --> H["Per-cluster\nFingerprint\nmedian price, tier mix\ngender mix, top cats\ntop brands, examples"]
    H --> I[/"llm/inputs/\nprofile_fingerprints.json\n12 aggregated summaries"/]
    F --> J[/"data/processed/\nproduct_clusters.parquet"/]

    style I fill:#fff3cd,stroke:#ff9800
```

### Stage 5 – Campaign Generation

```mermaid
flowchart TD
    A[/"profiles/profiles.json\n12 named profiles"/] --> B
    C[/"data/interim/universal/\nholdout split"/] --> B
    D[/"data/interim/edges/\nBOUGHT_WITH1"/] --> E["Bundle Map\npid → [co-purchased pids]"]

    B["For each of 12 profiles"]
    B --> F["Filter holdout pool\nto profile's affinity zone\n(dominant categories)"]
    F --> G["Score each candidate\n0.45×category\n+ 0.25×class\n+ 0.20×brand\n+ 0.10×price tier"]
    G --> H["For each of 52 weeks"]
    H --> I["Apply seasonality weight\naffinity × month_weight"]
    I --> J["Pick top-scoring\nunused item"]
    J --> K["Attach up to 3\nco-purchase bundles\nfrom Bundle Map"]
    K --> L{Week 52?}
    L -->|no| H
    L -->|yes| M[Next Profile]
    M --> N[/"data/processed/\ncampaign.parquet\n12 × 52 = 624 deals"/]
    E --> K
```

### Stage 6 – Valuation (CLV Model)

```mermaid
flowchart TD
    A[/"campaign.parquet"/] --> B
    C[/"profile_fingerprints.json"/] --> B

    B["Per profile × per week"]
    B --> D["base p = 0.06"]
    D --> E["× affinity_factor\n0.5 + affinity"]
    E --> F["× price_fit_factor\nprofile tier vs deal tier\nmatrix lookup"]
    F --> G["× season_factor\n0.7 + 0.3×season_weight"]
    G --> H["× fatigue_factor\n0.92^(week mod 8)\nresets bi-monthly"]
    H --> I["p_convert per deal\nclipped to 0..0.6"]

    I --> J["sum p_convert\nacross 52 weeks\n= raw_expected_orders"]
    J --> K["cap at\nbase_annual_orders\n× engagement\n= annual_purchase_cap"]
    K --> L["expected_annual_orders\n= min(raw, cap)"]
    L --> M["annual_value\n= orders × avg_order_value\n× gross_margin (0.45)"]
    M --> N[/"valuation_summary.csv\nCLV per profile"/]

    style N fill:#d4edda,stroke:#28a745
```

### LLM Integration Points

```mermaid
flowchart LR
    subgraph LLM1 ["🤖 LLM Step 1 — Brand Standardization (optional)"]
        A["data/reference/\nbrand_dicitonary.txt\n(R source file)"] --> B["make_brand_map.py\nextracts brand list\nwith item counts"]
        B --> C[/"llm/prompts/\nbrand_standardization\n_prompt.md"/]
        C --> D["Feed to LLM\n(aggregate brand list\nNOT raw records)"]
        D --> E[/"llm/outputs/\nbrand_overrides.json"/]
        E --> F["make brandmap\nbakes into brand_map.json\nO(1) dict lookup at runtime"]
    end

    subgraph LLM2 ["🤖 LLM Step 2 — Profile Naming (required)"]
        G[/"llm/inputs/\nprofile_fingerprints.json\n12 cluster summaries"/] --> H[/"llm/prompts/\nprofile_synthesis\n_prompt.md"/]
        H --> I["Feed to LLM\n(12 aggregates only\nNOT raw records)"]
        I --> J[/"profiles/profiles.json\n12 named personas"/]
        J --> K["render_profile_cards.py\n→ profiles/cards/*.md"]
    end

    style LLM1 fill:#fff3cd,stroke:#ff9800,stroke-width:2px
    style LLM2 fill:#fff3cd,stroke:#ff9800,stroke-width:2px
```

---

## Presentation

The capstone presentation is available as a PowerPoint file at [presentation/Amazon_Apparel_Capstone.pptx](presentation/Amazon_Apparel_Capstone.pptx).

It was generated programmatically from the pipeline data using [`presentation/build_ppt.js`](presentation/build_ppt.js) (Node.js + pptxgenjs). To regenerate it:

```bash
cd presentation
npm install
node build_ppt.js
```

### Slide Outline (15 slides)

| # | Slide | Coverage |
|---|-------|----------|
| 1 | **Cover** | Project title, 4 headline stats |
| 2 | **Problem & Framing** | Business problem, our framing, end-to-end pipeline flow |
| 3 | **The Data** | Record schema, two relationship signals (BW1/BW2), noise challenge, 70/30 split |
| 4 | **Handling Scale** | Streaming ingest, DuckDB out-of-core, disk-persisted intermediates |
| 5 | **Intelligence Layers** | Taxonomy, brand standardization, relationship graph — side by side |
| 6 | **Segmentation** | 5-step flow from products → 12 taste neighborhoods |
| 7 | **12 Profiles Grid** | All 12 profiles with derived names, tier, categories, brands, catalogue share |
| 8 | **Profile Deep-Dives** | Outerwear Enthusiast · Fitness-Forward Woman · Everyday Denim Dad |
| 9 | **Campaign Design** | Affinity scoring formula, seasonality logic, output schema |
| 10 | **Cadence vs Frequency** | 52 offers ≠ 52 purchases — fatigue decay and annual purchase cap |
| 11 | **Conversion Model** | 5-factor model: base × affinity × price-fit × season × fatigue |
| 12 | **Valuation Table** | All 12 profiles sorted by CLV with avg order value and expected orders |
| 13 | **Results at a Glance** | 6 headline KPIs + standout deals |
| 14 | **Limitations** | No transaction log · forced k=12 · holdout stub · assumption-driven priors |
| 15 | **Appendix** | Repo layout, reproducibility, config.yaml parameters |

---

## Repository Layout

```
amazon-apparel-capstone/
├── README.md               ← you are here
├── Makefile                ← make smoke / make all / make clean
├── requirements.txt
├── config.yaml             ← all tunable parameters (batch size, margins, tiers…)
│
├── src/
│   ├── config.py           ← loads config.yaml once → CFG dict
│   ├── taxonomy_assign.py  ← keyword-based category/class assignment
│   ├── brand_resolve.py    ← O(1) brand_map.json lookup
│   ├── seasonality.py      ← per-category month_weights
│   ├── stage01_ingest.py
│   ├── stage02_normalize.py
│   ├── stage03_intelligence.py
│   ├── stage04_segment.py
│   ├── stage05_campaign.py
│   └── stage06_valuation.py
│
├── scripts/
│   ├── make_brand_map.py       ← build brand_map.json from R dict + LLM overrides
│   ├── download_data.py        ← fetch corpus from Google Drive
│   ├── make_synthetic_corpus.py← generate synthetic data for smoke tests
│   └── render_profile_cards.py ← profiles.json → profiles/cards/*.md
│
├── data/
│   ├── raw/            # corpus (gitignored — too large)
│   ├── interim/        # parquet shards: products/, edges/, universal/ (gitignored)
│   ├── processed/      # final artifacts: brand_stats, campaign, valuation…
│   └── reference/      # taxonomy.py, brand_dicitonary.txt, brand_map.json
│
├── llm/
│   ├── prompts/        # brand_standardization_prompt.md, profile_synthesis_prompt.md
│   ├── inputs/         # profile_fingerprints.json (fed to LLM)
│   └── outputs/        # saved LLM responses (reproducibility)
│
├── profiles/
│   ├── profiles.json   # 12 named personas (LLM output)
│   └── cards/          # cluster_00.md … cluster_11.md (human-readable)
│
├── campaign/           # optional per-profile campaign exports
├── tests/              # pytest sanity checks
└── presentation/       # slide outline
```

---

## Key Design Decisions

| Decision | Why |
|----------|-----|
| **Stream ingest in 50k batches** | Corpus can be millions of records; fixed batch size keeps RAM flat on any machine |
| **70 / 30 discovery / holdout split** | Profiles are *discovered* on one half; weekly deals are *operated* on the other — no data leakage |
| **Two relationship signals** | `BOUGHT_WITH1` ("also bought", weight 1.0) is the backbone; `BOUGHT_WITH2` ("considered/liked", weight 0.35) adds signal but is down-weighted |
| **Real-brand floor (≥ 100 items)** | ~80k raw brand strings collapse to a few thousand real brands; long-tail noise is excluded from graph intelligence |
| **KMeans forced to 12** | Guarantees exactly 12 profiles as required; HDBSCAN would let count emerge organically (noted as a limitation) |
| **LLM offline only** | LLM never sees raw records — only 12 aggregated fingerprints. Every deterministic stage is reproducible with zero tokens |
| **Cadence ≠ frequency** | 52 weekly *offers* are generated, but expected annual *purchases* are capped realistically and decayed for offer fatigue |

---

## Outputs

| Artifact | Location | Description |
|----------|----------|-------------|
| Brand stats | `data/processed/brand_stats.parquet` | Item count, category breadth, price tier per brand |
| Brand co-occurrence | `data/processed/brand_cooccurrence.parquet` | Weighted brand↔brand purchase graph |
| Graph metrics | `data/processed/brand_graph_metrics.parquet` | Degree, eigen-centrality, betweenness per brand |
| Product clusters | `data/processed/product_clusters.parquet` | pid → cluster_id mapping |
| Profile fingerprints | `llm/inputs/profile_fingerprints.json` | 12 quantitative cluster summaries |
| Named profiles | `profiles/profiles.json` | 12 LLM-generated personas |
| Profile cards | `profiles/cards/cluster_XX.md` | Human-readable profile markdown |
| Campaign | `data/processed/campaign.parquet` | 12 × 52 deals with affinity + seasonality scores |
| Conversion detail | `data/processed/conversion_cluster_XX.parquet` | Per-deal conversion probability per profile |
| Valuation summary | `data/processed/valuation_summary.csv` | CLV estimate per profile |

---

## Limitations



- **No transaction log** — conversion is a *modelled, defended* estimate, not a measurement. All assumptions are in `config.yaml`.
- **KMeans forces exactly 12 clusters** — HDBSCAN would let the cluster count emerge from the data.
- **Holdout centroid-assignment is stubbed** — non-sampled products are not formally assigned to clusters in stage 4.
- **Seasonality, margin, and frequency priors are assumptions** — they are tunable in `config.yaml` but not validated against actuals.
- **Brand standardization is best-effort** — the R dictionary + optional LLM overrides do not cover every variant.
