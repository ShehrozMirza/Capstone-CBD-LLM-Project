#!/usr/bin/env python3
"""
stage02_normalize.py  --  apply taxonomy + brand standardization to every
product shard, derive price tier, and write the canonical "universal element"
table:  data/interim/universal/

Scales by processing one parquet shard at a time (RAM stays flat regardless of
corpus size). Pure deterministic transforms -- no LLM at run time.
"""
import glob
from pathlib import Path

import pandas as pd

from src.config import CFG
from src.taxonomy_assign import assign_category
from src.brand_resolve import BrandResolver


def _price_tier(p):
    if p is None or pd.isna(p):
        return "unknown"
    if p < 25:
        return "value"
    if p < 75:
        return "mid"
    return "premium"


def run():
    interim = Path(CFG["paths"]["interim_dir"])
    out_dir = interim / "universal"
    out_dir.mkdir(parents=True, exist_ok=True)

    resolver = BrandResolver(
        str(Path(CFG["paths"]["reference_dir"]) / "brand_map.json"))

    shards = sorted(glob.glob(str(interim / "products" / "*.parquet")))
    for i, shard in enumerate(shards):
        df = pd.read_parquet(shard)

        cats = df.apply(
            lambda r: assign_category(r["title"], r["desc"],
                                      (r["category_hierarchy"] or "").split(" > ")),
            axis=1, result_type="expand")
        df["category"] = cats[0]
        df["klass"] = cats[1]
        df["brand"] = df["brand_raw"].map(resolver.resolve)
        df["price_tier"] = df["retail_price"].map(_price_tier)

        keep = ["pid", "brand", "category", "klass", "gender", "color",
                "retail_price", "price_tier", "n_sizes", "split", "title"]
        df[keep].to_parquet(out_dir / f"part-{i:05d}.parquet", index=False)
        print(f"  normalized shard {i}: {len(df):,} rows")

    print(f"Wrote universal elements to {out_dir}")


if __name__ == "__main__":
    run()
