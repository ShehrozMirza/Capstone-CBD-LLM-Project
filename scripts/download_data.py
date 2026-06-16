#!/usr/bin/env python3
"""
download_data.py -- fetch + extract the corpus into data/raw/.

The data lives in a Google Drive folder (see the project brief). gdown handles
Drive folders. After download, extract any .zip shards in place.

    pip install gdown
    python scripts/download_data.py --folder <DRIVE_FOLDER_URL>

If your corpus is one-record-per-file JSON, they'll land under data/raw/ in
nested folders -- stage01 globs them recursively. If they're .jsonl shards,
stage01 streams them line by line. Either layout works.
"""
import argparse
import zipfile
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True, help="Google Drive folder URL")
    ap.add_argument("--out", default="data/raw")
    args = ap.parse_args()

    try:
        import gdown
    except ImportError:
        raise SystemExit("pip install gdown first")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    gdown.download_folder(args.folder, output=str(out), quiet=False, use_cookies=False)

    for z in out.rglob("*.zip"):
        print(f"extracting {z.name} ...")
        with zipfile.ZipFile(z) as zf:
            zf.extractall(z.parent)
    print("done.")


if __name__ == "__main__":
    main()
