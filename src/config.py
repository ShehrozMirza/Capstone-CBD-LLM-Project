"""Loads config.yaml once and exposes it as CFG."""
from pathlib import Path
import yaml

_ROOT = Path(__file__).resolve().parents[1]
with open(_ROOT / "config.yaml") as fh:
    CFG = yaml.safe_load(fh)

ROOT = _ROOT
