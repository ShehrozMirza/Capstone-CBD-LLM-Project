#!/usr/bin/env python3
"""render_profile_cards.py -- profiles.json -> profiles/cards/*.md (human-readable)."""
import json
from pathlib import Path


def main():
    src = Path("profiles/profiles.json")
    if not src.exists():
        raise SystemExit("profiles/profiles.json not found. Run the LLM profile "
                         "synthesis step first (see llm/prompts/profile_synthesis_prompt.md).")
    profiles = json.loads(src.read_text())
    out = Path("profiles/cards")
    out.mkdir(parents=True, exist_ok=True)
    for p in profiles:
        md = f"""# {p.get('name','Unnamed')}  (cluster {p.get('cluster_id')})

> {p.get('tagline','')}

**Income:** {p.get('approx_income','?')}  |  **Price posture:** {p.get('price_posture','?')}

**Demographics:** {p.get('demographics',{})}

**Style:** {p.get('style','')}

**Gravitates to:** {', '.join(p.get('categories_brands', []))}

**How they shop:** {p.get('how_they_shop','')}

**Evidence:** {p.get('evidence','')}
"""
        (out / f"cluster_{p.get('cluster_id'):02d}.md").write_text(md)
    print(f"wrote {len(profiles)} cards to {out}")


if __name__ == "__main__":
    main()
