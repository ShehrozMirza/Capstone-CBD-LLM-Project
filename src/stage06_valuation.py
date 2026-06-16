#!/usr/bin/env python3
"""
stage06_valuation.py  --  conversion model + annual customer value per profile.

No transaction log exists, so conversion is a DEFENDED model, not a measurement.

Per-deal conversion probability:
    p = base
        * affinity_factor      (stronger fit -> higher p)
        * price_fit_factor      (tier vs profile's price posture)
        * season_factor         (in-season deals convert better)
        * fatigue_factor        (each successive weekly offer worth a bit less)

Then we DECOUPLE offer cadence from purchase cadence:
    - 52 weekly offers, but a real customer buys only a handful of times/yr.
    - expected_orders = min( sum(p_week) , realistic annual cap for the profile )
    - annual_value = expected_orders * avg_order_value * gross_margin

Every assumption is in config.yaml and surfaced in the output for defense.

Run:
    python -m src.stage06_valuation
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import CFG

# price posture multipliers: how a profile's dominant tier reacts to each deal tier
TIER_FIT = {
    "value":   {"value": 1.00, "mid": 0.70, "premium": 0.35, "unknown": 0.6},
    "mid":     {"value": 0.85, "mid": 1.00, "premium": 0.65, "unknown": 0.7},
    "premium": {"value": 0.55, "mid": 0.85, "premium": 1.00, "unknown": 0.7},
}


def run():
    proc = Path(CFG["paths"]["processed_dir"])
    llm_in = Path(CFG["paths"]["llm_inputs"])
    v = CFG["valuation"]

    camp = pd.read_parquet(proc / "campaign.parquet")
    fps = {f["cluster_id"]: f for f in
           json.loads((llm_in / "profile_fingerprints.json").read_text())}

    base = 0.06   # base weekly-offer conversion before adjustments (stated assumption)
    rows = []
    for cid, g in camp.groupby("cluster_id"):
        fp = fps[cid]
        prof_tier = max(fp["price_tier_mix"], key=fp["price_tier_mix"].get) \
            if fp["price_tier_mix"] else "mid"
        prof_tier = prof_tier if prof_tier in TIER_FIT else "mid"

        g = g.sort_values("week").copy()
        # per-deal factors
        affinity_f = 0.5 + g["affinity"]                       # 0.5..1.5
        price_f = g["anchor_tier"].map(lambda t: TIER_FIT[prof_tier].get(t, 0.7))
        season_f = 0.7 + 0.3 * g["season_weight"].clip(0, 1.6) / 1.6
        fatigue_f = v["offer_fatigue_decay"] ** (np.arange(len(g)) % 8)  # resets ~ bi-monthly

        p = (base * affinity_f * price_f * season_f * fatigue_f).clip(0, 0.6)
        g["p_convert"] = p.values

        # decouple cadence: realistic annual purchase cap scaled by profile engagement
        engagement = float(np.mean(affinity_f))               # ~1.0
        annual_cap = v["base_annual_orders"] * engagement
        raw_orders = g["p_convert"].sum()
        expected_orders = min(raw_orders, annual_cap)

        avg_order_value = float(g["anchor_price"].mean())
        annual_value = expected_orders * avg_order_value * v["gross_margin"]

        rows.append({
            "cluster_id": cid,
            "profile_tier": prof_tier,
            "avg_deal_affinity": round(float(g["affinity"].mean()), 3),
            "avg_p_convert": round(float(g["p_convert"].mean()), 4),
            "raw_expected_orders_52wk": round(float(raw_orders), 2),
            "annual_purchase_cap": round(annual_cap, 2),
            "expected_annual_orders": round(expected_orders, 2),
            "avg_order_value": round(avg_order_value, 2),
            "gross_margin": v["gross_margin"],
            "annual_customer_value_clv": round(annual_value, 2),
        })

        # also persist per-deal conversion for transparency
        g[["cluster_id", "week", "anchor_pid", "anchor_tier",
           "affinity", "p_convert"]].to_parquet(
            proc / f"conversion_cluster_{cid:02d}.parquet", index=False)

    summary = pd.DataFrame(rows).sort_values("annual_customer_value_clv", ascending=False)
    summary.to_parquet(proc / "valuation_summary.parquet", index=False)
    summary.to_csv(proc / "valuation_summary.csv", index=False)
    print(summary.to_string(index=False))
    print(f"\nWrote valuation -> {proc/'valuation_summary.csv'}")


if __name__ == "__main__":
    run()
