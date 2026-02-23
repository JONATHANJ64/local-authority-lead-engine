from pathlib import Path

import site_generator.generate_site as generate_site


def test_render_pages_creates_expected_files(tmp_path, monkeypatch):
    site_root = tmp_path / "output"
    static_src = tmp_path / "static_src"
    static_src.mkdir()
    (static_src / "style.css").write_text("body{}", encoding="utf-8")

    monkeypatch.setattr(generate_site, "OUTPUT_DIR", str(site_root))
    monkeypatch.setattr(generate_site, "STATIC_SRC", str(static_src))

    niche_data = {
        "rank": 1,
        "niche": "Water Damage Restoration",
        "city": "Dallas",
        "cpc": 250.0,
        "difficulty": 10,
        "rationale": "test",
    }

    generate_site.render_pages(niche_data)

    site_slug = "water-damage-restoration_dallas"
    site_dir = site_root / site_slug

    assert (site_dir / "index.html").exists()
    assert (site_dir / "faq.html").exists()
    assert (site_dir / "sitemap.xml").exists()
    assert (site_dir / "robots.txt").exists()
    assert (site_dir / "static" / "style.css").exists()

    html = (site_dir / "index.html").read_text(encoding="utf-8")
    assert "application/ld+json" in html
    assert "action=\"/api/lead\"" in html
    assert "name=\"site_slug\"" in html

    robots = (site_dir / "robots.txt").read_text(encoding="utf-8")
    assert f"Sitemap: /{site_slug}/sitemap.xml" in robots

    sitemap = (site_dir / "sitemap.xml").read_text(encoding="utf-8")
    assert f"/{site_slug}/index.html" in sitemap


def test_load_top_niche_empty(tmp_path):
    json_path = tmp_path / "top_niches.json"
    json_path.write_text("[]", encoding="utf-8")

    try:
        generate_site.load_top_niche(str(json_path))
    except ValueError as exc:
        assert "No niche data found" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty niche data")
