# ============================================================
#  End-to-end pipeline. `make all` runs the deterministic path
#  (no LLM, no network) from raw data to valuation.
#  The two LLM steps are manual and slotted in where noted.
# ============================================================
PY = python

.PHONY: all brandmap ingest normalize intel segment campaign value clean smoke

## ---- one-time reference build (deterministic) ----
brandmap:
	$(PY) scripts/make_brand_map.py \
		--r-file data/reference/brand_dicitonary.txt \
		--overrides llm/outputs/brand_overrides.json \
		--out data/reference/brand_map.json || \
	$(PY) scripts/make_brand_map.py \
		--r-file data/reference/brand_dicitonary.txt \
		--out data/reference/brand_map.json

## ---- core pipeline (deterministic, no tokens) ----
ingest:    ; $(PY) -m src.stage01_ingest
normalize: ; $(PY) -m src.stage02_normalize
intel:     ; $(PY) -m src.stage03_intelligence
segment:   ; $(PY) -m src.stage04_segment
#   >>> LLM STEP 1: name the 12 profiles
#   feed llm/inputs/profile_fingerprints.json through
#   llm/prompts/profile_synthesis_prompt.md  ->  profiles/profiles.json
campaign:  ; $(PY) -m src.stage05_campaign
value:     ; $(PY) -m src.stage06_valuation

all: brandmap ingest normalize intel segment campaign value
	@echo "Pipeline complete. See data/processed/valuation_summary.csv"

## ---- smoke test on synthetic data (no download needed) ----
smoke:
	$(PY) scripts/make_synthetic_corpus.py --n 20000 --out data/raw
	$(MAKE) all

clean:
	rm -rf data/interim/* data/processed/* data/raw/synthetic.jsonl
