"""Scale Engine

This script reads the list of top niches from `data/top_niches.json` and
automatically generates a static site for each entry.  It calls the
`render_pages` function from `site_generator.generate_site` for each
niche/city combination.  This demonstrates the ability to clone the
infrastructure to multiple niches in a single run.

Usage:
    python scale_engine.py
"""
import json
import os

from site_generator.generate_site import render_pages, DATA_DIR, load_top_niche


def main() -> None:
    # Path to JSON with ranked niches
    json_path = os.path.join(DATA_DIR, "top_niches.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError("top_niches.json not found. Run niche_selection.py first.")
    with open(json_path, encoding="utf-8") as f:
        niches = json.load(f)
    for niche_data in niches:
        print(f"Generating site for {niche_data['niche']} in {niche_data['city']}...")
        render_pages(niche_data)
    print("All sites generated.")


if __name__ == "__main__":
    main()