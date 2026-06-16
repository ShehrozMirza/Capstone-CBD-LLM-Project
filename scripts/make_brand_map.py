#!/usr/bin/env python3
"""
make_brand_map.py
-----------------
The legacy brand standardization lives in an R file as hundreds of lines like:

    brand_list[which(brand_list %in% c("ADIDAS","ADIDAS GOLF",...))] <- "ADIDAS"

This script parses every such line and flattens it into a single deterministic
JSON lookup:  {"ADIDAS GOLF": "ADIDAS", "ADIDASORIGINALS": "ADIDAS", ...}

The runnable pipeline then does an O(1) dict lookup -- no R, no LLM, no rules
engine at run time. New mappings discovered by the LLM step (see llm/) are merged
in via data/reference/brand_overrides.json.

Usage:
    python scripts/make_brand_map.py \
        --r-file data/reference/brand_dicitonary.txt \
        --out    data/reference/brand_map.json
"""
import argparse
import json
import re
from pathlib import Path

# Matches:  ... %in% c( "A", "B", ... )) ] <- "CANONICAL"
LINE_RE = re.compile(
    r'%in%\s*c\((?P<variants>.*?)\)\s*\)\s*\]\s*<-\s*"(?P<canonical>[^"]+)"',
    re.DOTALL,
)
QUOTED_RE = re.compile(r'"([^"]*)"')


def normalize(s: str) -> str:
    """Same normalization applied to raw brand strings at run time."""
    s = s.upper().strip()
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)   # strip punctuation
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_r_file(text: str) -> dict:
    mapping = {}
    for m in LINE_RE.finditer(text):
        canonical = normalize(m.group("canonical"))
        if not canonical:
            continue
        for v in QUOTED_RE.findall(m.group("variants")):
            v = normalize(v)
            if v:
                mapping[v] = canonical
        mapping[canonical] = canonical  # canonical maps to itself
    return mapping


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--overrides", default=None,
                    help="optional LLM-produced overrides JSON merged on top")
    args = ap.parse_args()

    text = Path(args.r_file).read_text(encoding="utf-8", errors="ignore")
    mapping = parse_r_file(text)

    if args.overrides and Path(args.overrides).exists():
        extra = json.loads(Path(args.overrides).read_text())
        mapping.update({normalize(k): normalize(v) for k, v in extra.items()})

    Path(args.out).write_text(json.dumps(mapping, indent=0, sort_keys=True))
    print(f"Parsed {len(mapping):,} brand variants -> "
          f"{len(set(mapping.values())):,} canonical brands")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
