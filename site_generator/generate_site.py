"""
Site Generation Script
======================

This script implements Phase 2 of the Local Authority Lead Engine.  It reads the
list of niches produced by `niche_selection.py` and programmatically
generates a static website for a chosen niche and city.  The script uses
Jinja2 templates located in the `templates/` directory to render HTML pages
and writes the output into the `output/` directory.

For demonstration purposes, the script generates a site for the first entry
in the `data/top_niches.json` list (e.g., “Water Damage Restoration – Dallas”).
The generated site contains:

* **Homepage** – A general overview with service highlights and CTAs.
* **Service Pages** – Placeholder pages for sub‑services (e.g., water extraction, structural drying).
* **FAQ Page** – Frequently asked questions with schema.org FAQ markup.
* **sitemap.xml** and **robots.txt** – Basic files to aid search engine crawling.

The script can be extended to generate multiple sites or additional pages by
modifying the `pages` dictionary and the templates.
"""
import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(BASE_DIR), "output")

STATIC_SRC = os.path.join(BASE_DIR, "static")  # Directory containing CSS/JS assets


def load_top_niche(data_path: str) -> dict:
    """Load the top niche from the JSON data file.

    Args:
        data_path: Path to the JSON file created by `niche_selection.py`.

    Returns:
        A dictionary with keys: rank, niche, city, cpc, difficulty, rationale.
    """
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        raise ValueError("No niche data found. Run niche_selection.py first.")
    return data[0]


def render_pages(niche_data: dict) -> None:
    """Render all pages for a given niche and write them to disk.

    Args:
        niche_data: Dictionary of niche information.
    """
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    niche_slug = niche_data["niche"].lower().replace(" ", "-")
    city_slug = niche_data["city"].lower().replace(" ", "-")
    site_slug = f"{niche_slug}_{city_slug}"
    site_dir = os.path.join(OUTPUT_DIR, site_slug)
    os.makedirs(site_dir, exist_ok=True)

    # Define sub‑services (these can be expanded or generated via AI)
    sub_services = [
        {"name": "Water Extraction", "slug": "water-extraction", "description": "Rapid removal of standing water using industrial pumps and vacuums."},
        {"name": "Structural Drying", "slug": "structural-drying", "description": "Drying and dehumidification of walls, floors and other structural elements."},
        {"name": "Mold Remediation", "slug": "mold-remediation", "description": "Safe removal and prevention of mold and mildew growth."},
    ]

    # Common context for all templates
    context = {
        "niche": niche_data["niche"],
        "city": niche_data["city"],
        "phone": "(555) 123-4567",
        "sub_services": sub_services,
        "year": datetime.now().year,
        "site_slug": site_slug,
        "schema_business": json.dumps({
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": f"{niche_data['niche']} {niche_data['city']}",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": niche_data["city"],
                "addressRegion": "",  # Left blank; could insert state abbreviation
                "postalCode": "",
                "streetAddress": "",
            },
            "telephone": "(555) 123-4567",
            "priceRange": "$$$",
            "areaServed": {
                "@type": "City",
                "name": niche_data["city"]
            },
            "url": f"/{site_slug}/index.html"
        }, indent=2),
    }

    # Render homepage
    template = env.get_template("home.html")
    html = template.render(**context)
    with open(os.path.join(site_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # Render sub‑service pages
    service_template = env.get_template("service.html")
    for service in sub_services:
        service_ctx = context.copy()
        service_ctx.update(service)
        html = service_template.render(**service_ctx)
        service_path = os.path.join(site_dir, f"{service['slug']}.html")
        with open(service_path, "w", encoding="utf-8") as f:
            f.write(html)

    # Render FAQ page
    faq_template = env.get_template("faq.html")
    faq_ctx = context.copy()
    # Example FAQs – in practice these would be generated via AI
    faq_ctx["faqs"] = [
        {"question": f"How quickly can you respond to {context['niche'].lower()} emergencies?", "answer": "We offer 24/7 emergency response and aim to arrive within one hour of your call."},
        {"question": "Are your technicians certified?", "answer": "Yes, all of our technicians are IICRC‑certified and trained in the latest restoration techniques."},
        {"question": f"Do you work with insurance companies for {context['niche'].lower()} claims?", "answer": "We can coordinate directly with your insurer to streamline the claims process."},
    ]
    html = faq_template.render(**faq_ctx)
    with open(os.path.join(site_dir, "faq.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # Write sitemap.xml
    urls = ["index.html"] + [f"{s['slug']}.html" for s in sub_services] + ["faq.html"]
    sitemap_items = "\n".join([f"  <url><loc>/{site_slug}/{url}</loc></url>" for url in urls])
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap_items}\n</urlset>"""
    with open(os.path.join(site_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    # Write robots.txt
    robots = f"User-agent: *\nAllow: /\nSitemap: /{site_slug}/sitemap.xml\n"
    with open(os.path.join(site_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    # Copy static assets (CSS/JS) if available
    if os.path.exists(STATIC_SRC):
        import shutil
        static_dest = os.path.join(site_dir, "static")
        shutil.rmtree(static_dest, ignore_errors=True)
        shutil.copytree(STATIC_SRC, static_dest)

    print(f"Generated site for {niche_data['niche']} in {niche_data['city']} at {site_dir}")


def main():
    json_path = os.path.join(DATA_DIR, "top_niches.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"{json_path} not found. Run niche_selection.py first.")
    niche_data = load_top_niche(json_path)
    render_pages(niche_data)


if __name__ == "__main__":
    main()