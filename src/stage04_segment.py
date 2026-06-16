#!/usr/bin/env python3
"""
stage04_segment.py  --  discover 12 customer profiles.

There are no customers in the data, only products and product->product links.
So a "profile" is synthesized as a coherent *taste neighborhood*: a cluster of
products that share attributes AND co-purchase together. A customer of that type
is the person who shops that neighborhood.

Approach (deterministic, laptop-scale):
  1. Sample the discovery split (clustering is a non-scalable judgment step;
     we cluster a representative sample, then assign the rest by nearest centroid).
  2. Build a product feature vector: category/class, price tier, gender, brand
     graph centrality, brand price level.
  3. KMeans -> 12 clusters. (HDBSCAN is an alternative; KMeans guarantees 12.)
  4. For each cluster, compute a quantitative FINGERPRINT and write it to
     llm/inputs/profile_fingerprints.json -- the compact artifact the LLM names.

The LLM never sees raw records; only these 12 aggregated fingerprints.

Run:
    python -m src.stage04_segment
"""
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.config import CFG

SAMPLE_N = 300_000   # tune up/down for your RAM; representative, not exhaustive


def run():
    interim = Path(CFG["paths"]["interim_dir"])
    proc = Path(CFG["paths"]["processed_dir"])
    llm_in = Path(CFG["paths"]["llm_inputs"])
    llm_in.mkdir(parents=True, exist_ok=True)
    n_clusters = CFG["segmentation"]["n_profiles"]
    rs = CFG["segmentation"]["random_state"]

    con = duckdb.connect()
    uni = str(interim / "universal" / "*.parquet")

    # graph metrics are optional
    gm_path = proc / "brand_graph_metrics.parquet"
    has_gm = gm_path.exists()
    gm_join = (f"LEFT JOIN read_parquet('{gm_path}') gm ON u.brand = gm.brand"
               if has_gm else "")
    gm_cols = ("COALESCE(gm.eigen_centrality,0) AS brand_eigen, "
               "COALESCE(gm.weighted_degree,0)  AS brand_wdeg, "
               if has_gm else "0 AS brand_eigen, 0 AS brand_wdeg, ")

    df = con.execute(f"""
        SELECT u.pid, u.brand, u.category, u.klass, u.gender,
               u.retail_price, u.price_tier, {gm_cols}
               u.title
        FROM read_parquet('{uni}') u
        {gm_join}
        WHERE u.split='discovery' AND u.retail_price IS NOT NULL
        USING SAMPLE {SAMPLE_N} ROWS
    """).df()
    print(f"clustering sample: {len(df):,} products")

    # ---- feature matrix ----
    cat_oh = pd.get_dummies(df["category"], prefix="cat")
    tier_oh = pd.get_dummies(df["price_tier"], prefix="tier")
    gender_oh = pd.get_dummies(df["gender"].str.lower().fillna(""), prefix="g")
    num = df[["retail_price", "brand_eigen", "brand_wdeg"]].fillna(0)
    X = pd.concat([cat_oh, tier_oh, gender_oh, num], axis=1).fillna(0)
    Xs = StandardScaler().fit_transform(X)

    km = KMeans(n_clusters=n_clusters, random_state=rs, n_init=10)
    df["cluster"] = km.fit_predict(Xs)

    # ---- per-cluster fingerprints ----
    fingerprints = []
    for c in range(n_clusters):
        sub = df[df["cluster"] == c]
        fp = {
            "cluster_id": int(c),
            "size_share": round(len(sub) / len(df), 4),
            "median_price": round(float(sub["retail_price"].median()), 2),
            "price_tier_mix": sub["price_tier"].value_counts(normalize=True).round(3).to_dict(),
            "gender_mix": sub["gender"].str.lower().value_counts(normalize=True).round(3).head(3).to_dict(),
            "top_categories": sub["category"].value_counts(normalize=True).round(3).head(4).to_dict(),
            "top_classes": sub["klass"].value_counts(normalize=True).round(3).head(6).to_dict(),
            "top_brands": sub["brand"].value_counts().head(10).index.tolist(),
            "example_titles": sub["title"].dropna().head(5).tolist(),
        }
        fingerprints.append(fp)

    (llm_in / "profile_fingerprints.json").write_text(json.dumps(fingerprints, indent=2))
    df[["pid", "cluster"]].to_parquet(proc / "product_clusters.parquet", index=False)
    # persist centroids + scaler params would go here for holdout assignment
    print(f"Wrote 12 fingerprints -> {llm_in/'profile_fingerprints.json'}")
    con.close()


if __name__ == "__main__":
    run()
