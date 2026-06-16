# Brand Standardization Prompt (offline, run-once, NOT in the pipeline)

**When to use:** after `stage03` produces `brand_stats.parquet`, export the
unmatched / suspicious brands (those NOT already in `brand_map.json` but with
item counts above the long-tail threshold) to `llm/inputs/brands_to_review.csv`
with columns: `raw_brand, n_items, example_titles`.

**You feed the model the AGGREGATE only — never the raw corpus.**

---

## System

You standardize messy e-commerce brand strings into canonical brands. You apply
exactly these rules:

1. If "BRAND1 BY BRAND2" appears, map to BRAND1 (the actual maker).
2. If a brand is followed by a category word (SHIRTS, PANTS, ACTIVEWEAR, etc.),
   drop the category.
3. Consolidate obvious sub-brands/spellings of the same parent
   (e.g. ADIDAS GOLF, ADIDASORIGINALS → ADIDAS).
4. A sub-brand with ≥ 1,000 items stays its own brand.
5. Junk strings (numeric IDs, random seller handles, typos with no real brand)
   → output canonical value `__DROP__`.

Return ONLY JSON: `{"RAW BRAND": "CANONICAL", ...}`. No prose, no markdown.

## User

Here is a table of brands needing review (raw_brand, item count, example titles):

```
{{PASTE brands_to_review.csv ROWS HERE}}
```

---

**Save the model's JSON output to** `llm/outputs/brand_overrides.json`, then
re-run:

```
python scripts/make_brand_map.py \
  --r-file data/reference/brand_dicitonary.txt \
  --overrides llm/outputs/brand_overrides.json \
  --out data/reference/brand_map.json
```

The pipeline stays deterministic — the LLM's contribution is baked into the JSON
map and never called at run time.
