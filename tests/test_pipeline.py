"""Minimal sanity tests. Run: python -m pytest tests/ -q"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.brand_resolve import BrandResolver
from src.taxonomy_assign import assign_category


def test_brand_subbrand_folding():
    r = BrandResolver("data/reference/brand_map.json")
    assert r.resolve("AIR JORDAN") == "NIKE"
    assert r.resolve("adidas golf") == "ADIDAS"
    assert r.resolve("ABS by Allen Schwartz") == "ALLEN SCHWARTZ"


def test_brand_suffix_strip():
    r = BrandResolver("data/reference/brand_map.json")
    # unknown brand + category suffix -> stem kept
    assert r.resolve("SomeBrand Tops Blouses") == "SOMEBRAND"


def test_taxonomy_assignment():
    cat, klass = assign_category(
        "Columbia Men's PFG Super Bahama Short Sleeve Shirt", "fishing shirt",
        ["Clothing", "Men", "Shirts", "Casual Button-Down Shirts"])
    assert cat == "upperbody"
    assert klass in ("shirts", "polos", "t_shirts")
