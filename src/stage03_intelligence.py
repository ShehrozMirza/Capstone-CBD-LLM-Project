#!/usr/bin/env python3
"""
stage03_intelligence.py  --  build the data fabric.

Uses DuckDB so aggregations run out-of-core (larger-than-RAM safe) straight off
the parquet shards. Produces, for the DISCOVERY split:

  1. brand_stats           -- item counts, category breadth, price tiers, "real" flag
  2. item_universal        -- joined product attributes + canonical brand/class
  3. brand_cooccurrence    -- brand<->brand weighted edges from BOUGHT_WITH1/2
  4. brand_graph_metrics   -- degree, weighted degree, eigenvector centrality

The graph metrics are FEATURES that feed segmentation -- not the deliverable.

Run:
    python -m src.stage03_intelligence
"""
from pathlib import Path

import duckdb
import pandas as pd

from src.config import CFG


def run():
    interim = Path(CFG["paths"]["interim_dir"])
    proc = Path(CFG["paths"]["processed_dir"])
    proc.mkdir(parents=True, exist_ok=True)

    uni = str(interim / "universal" / "*.parquet")
    edges = str(interim / "edges" / "*.parquet")
    bw1 = CFG["relationships"]["bw1_weight"]
    bw2 = CFG["relationships"]["bw2_weight"]
    min_edge = CFG["relationships"]["min_edge_count"]
    min_real = CFG["brands"]["min_items_real"]

    con = duckdb.connect()
    con.execute(f"CREATE VIEW u AS SELECT * FROM read_parquet('{uni}')")
    con.execute(f"CREATE VIEW e AS SELECT * FROM read_parquet('{edges}')")
    con.execute("CREATE VIEW ud AS SELECT * FROM u WHERE split='discovery'")

    # 1. brand stats + "real brand" flag (drops the long tail)
    con.execute(f"""
        CREATE TABLE brand_stats AS
        SELECT brand,
               COUNT(*)                         AS n_items,
               COUNT(DISTINCT category)         AS n_categories,
               COUNT(DISTINCT klass)            AS n_classes,
               MEDIAN(retail_price)             AS median_price,
               MODE(price_tier)                 AS dominant_tier,
               (COUNT(*) >= {min_real})         AS is_real
        FROM ud
        WHERE brand <> ''
        GROUP BY brand
        ORDER BY n_items DESC
    """)
    con.execute(f"COPY brand_stats TO '{proc/'brand_stats.parquet'}' (FORMAT parquet)")

    # 2. brand<->brand co-occurrence (weighted by edge type), real brands only
    con.execute(f"""
        CREATE TABLE brand_cooc AS
        WITH real AS (SELECT brand FROM brand_stats WHERE is_real),
        edge_brands AS (
            SELECT us.brand AS b_src, ud2.brand AS b_dst,
                   CASE WHEN e.kind=1 THEN {bw1} ELSE {bw2} END AS w
            FROM e
            JOIN u  us  ON e.src = us.pid
            JOIN u  ud2 ON e.dst = ud2.pid
            WHERE us.split='discovery'
              AND us.brand IN (SELECT brand FROM real)
              AND ud2.brand IN (SELECT brand FROM real)
              AND us.brand <> ud2.brand
        )
        SELECT b_src, b_dst, SUM(w) AS weight, COUNT(*) AS cnt
        FROM edge_brands
        GROUP BY b_src, b_dst
        HAVING COUNT(*) >= {min_edge}
    """)
    con.execute(f"COPY brand_cooc TO '{proc/'brand_cooccurrence.parquet'}' (FORMAT parquet)")

    # 3. category<->category co-occurrence (for campaign cross-sell logic)
    con.execute(f"""
        CREATE TABLE cat_cooc AS
        SELECT us.klass AS k_src, ud2.klass AS k_dst,
               SUM(CASE WHEN e.kind=1 THEN {bw1} ELSE {bw2} END) AS weight
        FROM e
        JOIN u us  ON e.src = us.pid
        JOIN u ud2 ON e.dst = ud2.pid
        WHERE us.split='discovery' AND us.klass <> ud2.klass
        GROUP BY us.klass, ud2.klass
    """)
    con.execute(f"COPY cat_cooc TO '{proc/'category_cooccurrence.parquet'}' (FORMAT parquet)")

    print("brand_stats rows :", con.execute("SELECT COUNT(*) FROM brand_stats").fetchone()[0])
    print("real brands      :", con.execute("SELECT COUNT(*) FROM brand_stats WHERE is_real").fetchone()[0])
    print("brand cooc edges :", con.execute("SELECT COUNT(*) FROM brand_cooc").fetchone()[0])

    # 4. graph centrality with igraph (feature, not deliverable)
    _graph_metrics(con, proc)
    con.close()


def _graph_metrics(con, proc):
    try:
        import igraph as ig
    except ImportError:
        print("python-igraph not installed; skipping centrality (optional).")
        return
    edf = con.execute("SELECT b_src, b_dst, weight FROM brand_cooc").df()
    if edf.empty:
        print("no brand edges; skipping centrality.")
        return
    g = ig.Graph.TupleList(edf.itertuples(index=False), weights=True, directed=False)
    metrics = pd.DataFrame({
        "brand": g.vs["name"],
        "degree": g.degree(),
        "weighted_degree": g.strength(weights="weight"),
        "eigen_centrality": g.eigenvector_centrality(weights="weight"),
        "betweenness": g.betweenness(weights="weight"),
    })
    metrics.to_parquet(proc / "brand_graph_metrics.parquet", index=False)
    print(f"graph metrics    : {len(metrics):,} brands "
          f"(top hub: {metrics.sort_values('eigen_centrality', ascending=False).iloc[0]['brand']})")


if __name__ == "__main__":
    run()
