"""
Category assignment. Given a product's text fields, find the best
(category, class) by scanning the taxonomy trigger synonyms.

Strategy:
  1. Trust the retailer's own categoryHierarchy first when it maps cleanly.
  2. Fall back to title/desc keyword triggers.
  3. Longer, more specific trigger phrases win over short generic ones.

This is pure deterministic string matching -- scales linearly, no LLM.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data" / "reference"))
from taxonomy import CATS  # noqa: E402

# Pre-compile: list of (category, klass, trigger, specificity) sorted long->short
_TRIGGERS = []
for _cat, _classes in CATS.items():
    for _klass, _syns in _classes.items():
        # the class name itself is always a trigger
        _TRIGGERS.append((_cat, _klass, _klass.replace("_", " "), len(_klass)))
        for _s in _syns:
            _TRIGGERS.append((_cat, _klass, _s.lower(), len(_s)))
_TRIGGERS.sort(key=lambda t: t[3], reverse=True)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower())


def assign_category(title: str, desc: str, category_hierarchy=None):
    """Return (category, klass) or ('assorted', 'other') if nothing matches."""
    hay = _clean(" ".join(filter(None, [
        title,
        " ".join(category_hierarchy or []),
        (desc or "")[:400],   # cap desc scan -- keeps it fast on huge corpora
    ])))

    for cat, klass, trigger, _spec in _TRIGGERS:
        # word-boundary-ish match; leading-space triggers (" bra") matched as-is
        if trigger.startswith(" "):
            if trigger in hay:
                return cat, klass
        elif re.search(r"\b" + re.escape(trigger) + r"\b", hay):
            return cat, klass
    return "assorted", "other"


if __name__ == "__main__":
    # smoke test against the sample record
    cat, klass = assign_category(
        "Columbia Men's PFG Super Bahama Short Sleeve Shirt, Breathable, UV Protection",
        "Columbia's PFG line ... fishing shirt ...",
        ["Clothing, Shoes & Jewelry", "Men", "Clothing", "Shirts", "Casual Button-Down Shirts"],
    )
    print(f"sample -> {cat} / {klass}")
