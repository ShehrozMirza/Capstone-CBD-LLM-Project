#!/usr/bin/env python3
"""
stage05_campaign.py  --  year-long weekly deal campaign per profile.

For each of the 12 profiles (cluster fingerprints), generate 52 weekly deals
drawn from REAL items in the HELD-OUT split, sequenced by seasonality, with
co-purchase bundles attached via BOUGHT_WITH1.

Output: data/processed/campaign.parquet
  columns: cluster_id, week, anchor_pid, anchor_title, anchor_brand,
           anchor_category, anchor_price, bundle_pids, affinity, season_weight

Deals trace back to the intelligence: candidates are filtered to the profile's
affinity zone (its dominant categories/brands/price tier), ranked by an affinity
score, and bundles come from the real co-purchase graph.

Run:
    python -m src.stage05_campaign
"""
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from src.config import CFG
from src.seasonality import SEASON, week_to_month


def _affinity(row, fp):
    """Score how well a holdout item fits a profile fingerprint (0..1)."""
    s = 0.0
    s += 0.45 * fp["top_categories"].get(row["category"], 0.0)
    s += 0.25 * fp["top_classes"].get(row["klass"], 0.0)
    s += 0.20 * (1.0 if row["brand"] in fp["top_brands"] else 0.0)
    s += 0.10 * fp["price_tier_mix"].get(row["price_tier"], 0.0)
    return min(1.0, s)


def run():
    interim = Path(CFG["paths"]["interim_dir"])
    proc = Path(CFG["paths"]["processed_dir"])
    llm_in = Path(CFG["paths"]["llm_inputs"])

    fingerprints = json.loads((llm_in / "profile_fingerprints.json").read_text())

    con = duckdb.connect()
    uni = str(interim / "universal" / "*.parquet")
    edges = str(interim / "edges" / "*.parquet")

    # holdout candidate pool (pull a manageable, attribute-rich slice)
    pool = con.execute(f"""
        SELECT pid, brand, category, klass, price_tier, retail_price, title
        FROM read_parquet('{uni}')
        WHERE split='holdout' AND retail_price IS NOT NULL
    """).df()

    # co-purchase lookup for bundles (BOUGHT_WITH1 only = strong signal)
    bw1 = con.execute(f"""
        SELECT src, dst FROM read_parquet('{edges}') WHERE kind=1
    """).df()
    bundle_map = bw1.groupby("src")["dst"].apply(list).to_dict()
    valid_pids = set(pool["pid"])

    rows = []
    for fp in fingerprints:
        cid = fp["cluster_id"]
        # restrict to this profile's affinity zone for speed
        zone = pool[pool["category"].isin(fp["top_categories"].keys())].copy()
        if zone.empty:
            zone = pool.copy()
        zone["affinity"] = zone.apply(lambda r: _affinity(r, fp), axis=1)
        zone = zone[zone["affinity"] > 0].sort_values("affinity", ascending=False)

        used = set()
        for week in range(1, 53):
            month = week_to_month(week)
            # re-rank by affinity * this month's seasonality for the item's category
            def season_w(cat):
                return SEASON.get(cat, SEASON["assorted"])["month_weights"].get(month, 1.0)
            cand = zone[~zone["pid"].isin(used)].copy()
            if cand.empty:
                cand = zone.copy()
            cand["season_weight"] = cand["category"].map(season_w)
            cand["score"] = cand["affinity"] * cand["season_weight"]
            pick = cand.sort_values("score", ascending=False).iloc[0]
            used.add(pick["pid"])

            bundle = [p for p in bundle_map.get(pick["pid"], [])[:3] if p in valid_pids]
            rows.append({
                "cluster_id": cid, "week": week, "month": month,
                "anchor_pid": pick["pid"], "anchor_title": pick["title"],
                "anchor_brand": pick["brand"], "anchor_category": pick["category"],
                "anchor_klass": pick["klass"], "anchor_price": float(pick["retail_price"]),
                "anchor_tier": pick["price_tier"],
                "bundle_pids": ",".join(bundle),
                "affinity": round(float(pick["affinity"]), 4),
                "season_weight": round(float(season_w(pick["category"])), 3),
            })

    out = pd.DataFrame(rows)
    out.to_parquet(proc / "campaign.parquet", index=False)
    print(f"Wrote {len(out):,} deals ({out['cluster_id'].nunique()} profiles x 52 weeks) "
          f"-> {proc/'campaign.parquet'}")
    con.close()


if __name__ == "__main__":
    run()
