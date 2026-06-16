"""
Brand standardization at run time. Pure dict lookup + cheap deterministic
fallback rules. No LLM, no R. The dict (brand_map.json) is produced offline
by scripts/make_brand_map.py and optionally enriched by the LLM step.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

_CATEGORY_SUFFIXES = [
    "ACTIVEWEAR BOTTOMS", "ACTIVEWEAR TOPS", "TOPS BLOUSES", "CASUAL SHIRTS",
    "DRESS SHIRTS", "COATS JACKETS", "SPORTS BRAS", "SWEATERS", "TSHIRTS",
    "PANTS", "SKIRTS", "TOPS", "JEANS", "SHOES", "INC", "LLC", "CORP",
]


def _normalize(s: str) -> str:
    s = (s or "").upper().strip()
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


class BrandResolver:
    def __init__(self, brand_map_path: str):
        self.map = json.loads(Path(brand_map_path).read_text())

    @lru_cache(maxsize=200_000)
    def resolve(self, raw_brand: str) -> str:
        b = _normalize(raw_brand)
        if not b:
            return ""
        # 1. exact known mapping
        if b in self.map:
            return self.map[b]
        # 2. "brand1 by brand2" -> brand1
        if " BY " in b:
            head = b.split(" BY ")[0].strip()
            return self.map.get(head, head)
        # 3. strip trailing category suffix, retry
        for suf in _CATEGORY_SUFFIXES:
            if b.endswith(" " + suf):
                stem = b[: -(len(suf) + 1)].strip()
                return self.map.get(stem, stem)
        # 4. unknown -> keep normalized form (filtered later if long-tail)
        return b


if __name__ == "__main__":
    import sys
    r = BrandResolver(sys.argv[1] if len(sys.argv) > 1
                      else "data/reference/brand_map.json")
    for t in ["Columbia", "adidas golf", "ABS by Allen Schwartz",
              "Nike Performance Tops Blouses", "SomeRandomSeller123"]:
        print(f"{t!r:35} -> {r.resolve(t)!r}")
