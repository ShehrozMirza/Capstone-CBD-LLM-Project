# Presentation Outline (~12–18 slides)

Maps 1:1 to the brief's §8B required coverage. Build in PowerPoint/Slides;
pull numbers from `data/processed/`.

1. **Title** — project name, your name, one-line thesis.
2. **The problem & framing** — millions of raw Amazon apparel records → named
   profiles → a year of deals with defensible value. What "intelligence" means here.
3. **The data** — record schema; the two relationship signals (BW1 strong / BW2 weak);
   the noise (80k brand strings, inconsistent categories).
4. **Handling scale (and why it scales)** — streaming ingest in 50k batches → parquet;
   DuckDB out-of-core aggregation; disk-persisted intermediates; "would survive 100×."
5. **Taxonomy layer** — synonym-trigger category→class assignment; coverage stats;
   what % landed in `assorted/other` and why.
6. **Brand standardization** — R rules → flattened JSON map (1,318→376); the LLM
   aggregate step for the long tail; the real-brand floor (≥100 items).
7. **Relationship intelligence** — brand↔brand & category↔category co-occurrence;
   graph centrality (hubs/bridges) as *features*, not the deliverable.
8. **From products to people** — the segmentation logic: taste neighborhoods,
   the resolution tension (1 average shopper vs 12 noise clusters), how 12 emerged.
9–11. **The 12 profiles** (≈2 slides) — a grid of persona cards: name, income,
   style, categories/brands, price posture, how they shop. Show 2–3 in detail.
12. **Campaign design** — 52 weekly deals per profile; bundles from BW1;
    seasonality scheduling; a sample profile's calendar.
13. **Cadence vs frequency** — the core modeling slide: 52 offers ≠ 52 purchases;
    fatigue decay; realistic ~3–6 orders/yr cap.
14. **Conversion model** — affinity × price-fit × season × fatigue; why each factor;
    how it's defensible without ground truth.
15. **Valuation / CLV** — expected annual orders × AOV × margin; the per-profile
    table sorted by CLV; which profiles are most valuable and why.
16. **Results** — headline numbers; premium vs value spread; a couple of standout deals.
17. **Limitations** — no transaction log, forced k=12, assumption-driven priors,
    holdout assignment stub. What you'd do with more time/data.
18. **Appendix** — repo structure, reproducibility, LLM prompt artifacts.
