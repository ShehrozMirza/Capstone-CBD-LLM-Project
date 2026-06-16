#!/usr/bin/env python3
"""
stage01_ingest.py  --  raw JSON in, clean columnar parquet out.

Scalability contract:
  * Streams the corpus in fixed-size batches; never loads it all into RAM.
  * Writes parquet shards to data/interim/products/ as it goes.
  * Also emits a long-form edge list (data/interim/edges/) of every
    product->product BOUGHT_WITH link, which is the raw material for all
    relationship intelligence. Edges are written incrementally too.

Supports two corpus layouts (auto-detected):
  A) millions of individual *.json files in nested folders  (glob)
  B) *.jsonl shards, one record per line                    (line stream)

Run:
    python -m src.stage01_ingest
"""
import gc
import glob
import hashlib
import json
import os
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.config import CFG


def _iter_records(raw_dir: str, pattern: str):
    """Yield raw dict records from either *.json files or *.jsonl shards."""
    jsonl = glob.glob(os.path.join(raw_dir, "**", "*.jsonl"), recursive=True)
    if jsonl:
        for shard in jsonl:
            with open(shard, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue
    else:
        for fp in glob.iglob(os.path.join(raw_dir, pattern), recursive=True):
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                    yield json.load(fh)
            except (json.JSONDecodeError, OSError):
                continue


def _split_bucket(pid: str, seed: int) -> str:
    """Deterministic discovery/holdout split by hashing the product id."""
    h = int(hashlib.md5(f"{seed}:{pid}".encode()).hexdigest(), 16)
    frac = (h % 10_000) / 10_000.0
    return "discovery" if frac < CFG["split"]["discovery_frac"] else "holdout"


def _flat(rec: dict, seed: int):
    pid = rec.get("retailerProductId")
    title = rec.get("title") or ""
    if not pid or len(title) < CFG["ingest"]["min_title_len"]:
        return None, []

    sizes = rec.get("size") or []
    row = {
        "pid": pid,
        "title": title,
        "desc": (rec.get("desc") or "")[:2000],   # cap stored desc
        "brand_raw": rec.get("brand") or "",
        "gender": rec.get("gender") or "",
        "color": rec.get("color") or "",
        "category_hierarchy": " > ".join(rec.get("categoryHierarchy") or []),
        "retail_price": rec.get("retailPrice"),
        "price_range": rec.get("priceRange") or "",
        "n_sizes": len(sizes),
        "split": _split_bucket(pid, seed),
    }

    edges = []
    rel = rec.get("relatedProducts") or {}
    for kind, w in (("BOUGHT_WITH1", 1), ("BOUGHT_WITH2", 2)):
        for item in rel.get(kind, []) or []:
            tgt = item.get("retailerProductId")
            if tgt:
                edges.append({"src": pid, "dst": tgt, "kind": w})
    return row, edges


def run():
    raw_dir = CFG["paths"]["raw_dir"]
    interim = Path(CFG["paths"]["interim_dir"])
    prod_dir = interim / "products"
    edge_dir = interim / "edges"
    prod_dir.mkdir(parents=True, exist_ok=True)
    edge_dir.mkdir(parents=True, exist_ok=True)

    batch_size = CFG["ingest"]["batch_size"]
    seed = CFG["split"]["seed"]
    pattern = CFG["ingest"]["glob_pattern"]

    prod_buf, edge_buf, shard, n = [], [], 0, 0
    for rec in _iter_records(raw_dir, pattern):
        row, edges = _flat(rec, seed)
        if row is None:
            continue
        prod_buf.append(row)
        edge_buf.extend(edges)
        n += 1
        if len(prod_buf) >= batch_size:
            _flush(prod_buf, edge_buf, prod_dir, edge_dir, shard)
            prod_buf, edge_buf = [], []
            shard += 1
            gc.collect()
    if prod_buf:
        _flush(prod_buf, edge_buf, prod_dir, edge_dir, shard)

    print(f"Ingested {n:,} records into {shard + 1} parquet shard(s).")


def _flush(prod_buf, edge_buf, prod_dir, edge_dir, shard):
    pq.write_table(pa.Table.from_pandas(pd.DataFrame(prod_buf)),
                   prod_dir / f"part-{shard:05d}.parquet")
    if edge_buf:
        pq.write_table(pa.Table.from_pandas(pd.DataFrame(edge_buf)),
                       edge_dir / f"part-{shard:05d}.parquet")
    print(f"  shard {shard}: {len(prod_buf):,} products, {len(edge_buf):,} edges")


if __name__ == "__main__":
    run()
