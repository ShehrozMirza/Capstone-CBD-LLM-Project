#!/usr/bin/env python3
"""
make_synthetic_corpus.py -- generate a small fake corpus shaped exactly like the
real records so the whole pipeline can be smoke-tested with no download.

    python scripts/make_synthetic_corpus.py --n 20000 --out data/raw

Produces data/raw/synthetic.jsonl (one record per line).
"""
import argparse
import json
import random
from pathlib import Path

BRANDS = ["Columbia", "ADIDAS GOLF", "Nike Performance", "Levi's", "Calvin Klein",
          "Hanes", "Under Armour", "Patagonia", "ABS BY ALLEN SCHWARTZ",
          "Ralph Lauren", "RandomSeller7723", "Gucci", "Old Navy", "Wrangler"]
TITLES = [
    ("Men's Short Sleeve Fishing Shirt UV Protection", "upperbody", 25, "Men"),
    ("Women's High Waist Yoga Leggings", "lowerbody", 35, "Women"),
    ("Running Shoes Lightweight Sneakers", "footwear", 80, "Unisex"),
    ("Winter Down Parka Coat Insulated", "outerwear", 180, "Women"),
    ("Classic Fit Denim Jeans", "lowerbody", 45, "Men"),
    ("Bikini Swimwear Two Piece", "swimwear", 30, "Women"),
    ("Cotton Crew Neck T-Shirt", "upperbody", 12, "Men"),
    ("Leather Crossbody Bag Handbag", "accessories", 120, "Women"),
    ("Wool Blend Cardigan Sweater", "upperbody", 60, "Women"),
    ("Performance Polo Collared Shirt", "upperbody", 40, "Men"),
]
COLORS = ["Black", "Navy Blue", "Heather Grey", "Vivid Red", "Olive Green", "White"]
SIZES = ["X-Small", "Small", "Medium", "Large", "X-Large", "XX-Large"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--out", default="data/raw")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    pids = [f"B{random.randint(10**9, 10**10-1):010X}"[:11] for _ in range(args.n)]
    with open(out / "synthetic.jsonl", "w") as fh:
        for i, pid in enumerate(pids):
            base, cat, price, gender = random.choice(TITLES)
            brand = random.choice(BRANDS)
            price_j = round(price * random.uniform(0.7, 1.6), 2)
            bw1 = [{"retailerProductId": p} for p in random.sample(pids, k=random.randint(3, 12))]
            bw2 = [{"retailerProductId": p} for p in random.sample(pids, k=random.randint(0, 4))]
            rec = {
                "retailer": "amazon", "retailerProductId": pid,
                "url": f"https://www.amazon.com/dp/{pid}",
                "title": f"{brand} {base}",
                "desc": f"{brand} quality {base.lower()} made with premium materials.",
                "categoryHierarchy": ["Clothing, Shoes & Jewelry", gender, "Clothing"],
                "gender": gender, "brand": brand,
                "color": random.choice(COLORS),
                "size": random.sample(SIZES, k=random.randint(2, 6)),
                "retailPrice": price_j,
                "priceRange": f"${price_j} - ${round(price_j*2,2)}",
                "images": [],
                "relatedProducts": {"BOUGHT_WITH1": bw1, "BOUGHT_WITH2": bw2},
            }
            fh.write(json.dumps(rec) + "\n")
    print(f"wrote {args.n:,} synthetic records to {out/'synthetic.jsonl'}")


if __name__ == "__main__":
    main()
