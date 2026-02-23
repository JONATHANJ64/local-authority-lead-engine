import json
from pathlib import Path

import niche_selection


def test_niche_selection_main_outputs_files():
    niche_selection.main()
    data_dir = Path(__file__).resolve().parents[1] / "data"
    json_path = data_dir / "top_niches.json"
    csv_path = data_dir / "top_niches.csv"

    assert json_path.exists()
    assert csv_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 1


def test_filter_niches_thresholds_edge_case():
    niches = niche_selection.get_seed_data()
    filtered = niche_selection.filter_niches(niches, min_cpc=1000.0, max_difficulty=1)
    assert filtered == []
