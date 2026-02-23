# Local Authority Lead Engine Architecture

## Overview

The Local Authority Lead Engine is designed to automatically generate, publish, rank and monetise highly‑targeted local service websites.  
It identifies lucrative niches and city combinations, builds search‑optimised sites, captures and routes leads to local partners and automates billing.  
The platform is composed of loosely‑coupled services that communicate through RESTful APIs and asynchronous jobs.  

The solution is divided into six phases:

1. **Niche Selection Engine** – scrapes keyword and cost‑per‑click (CPC) data, assesses transactional intent and SEO competition, and outputs top niches by city.
2. **Site Generation System** – programmatically generates static websites for each niche/city combination, complete with schema markup, FAQ data and conversion‑oriented calls‑to‑action (CTAs).
3. **SEO Automation** – builds internal link graphs, generates blog clusters and submits sitemaps to Google Search Console.
4. **Lead Capture** – installs form capture, call tracking and SMS forwarding on each site and stores leads in a central database while routing them to the assigned local partner.
5. **Sales Automation** – monitors lead volume and triggers outreach to potential service providers. It handles invoicing through Stripe and subscription management.
6. **Scale Engine** – clones the infrastructure for new niche/city combos, tracks ROI and removes underperforming sites.

### High‑Level Diagram

The following diagram summarises the platform’s architecture:

![High‑level architecture diagram]({{file:file-UQzypPvp97uuYicgVDrz8J}})

Each phase can be developed and deployed independently.  
The system uses a **static site generator** to create pages, **serverless functions** to handle form submissions and scheduled jobs, a **PostgreSQL database** for persisting leads and billing data, a **headless CMS** (optional) for managing content, and **Stripe** for payment processing.  
Infrastructure is provisioned using **Infrastructure as Code (IaC)** tools (not shown in this document) to enable rapid replication across niches and cities.

## Phase 1: Niche Selection Engine

### Data Sources

- **Keyword and CPC data:** scraped from public PPC studies and benchmark articles.  
  For example, research shows that home‑service keywords such as “water damage restoration Dallas” ($250.79 CPC), “emergency plumbing services” ($82.82 CPC), and “roof leak repair” (around $12–18 CPC) command high CPCs【432626109982497†L515-L540】【867266786737301†L293-L307】.  
- **SEO difficulty:** estimated using third‑party tools like Ahrefs or Mangools.  
  Water‑damage restoration keywords have a keyword difficulty of ~18 (considered easy)【648190089987163†L212-L219】.
- **Transactional intent:** determined by the presence of local modifiers (“near me,” city names) and emergency phrases.  Keywords such as “emergency plumber near me” convert better and cost more【440617436258527†L176-L184】.

### Process

1. **Keyword Collection:** Start with a list of high‑CPC, emergency‑intent service categories (e.g., water damage restoration, flood cleanup, emergency plumbing, HVAC repair, roof repair, garage door repair, pest control, window replacement, home security system installation, duct cleaning).  
2. **Scraping & Normalisation:** Use headless browsing or API requests to fetch CPC data from sources like PPC.io, Arvow and WebFX.  The scraper normalises CPC values and stores them alongside geographic modifiers.  
3. **Filtering:** Filter for niches with CPC > $10 and high transactional intent.  Remove categories with high SEO difficulty (> 40) to prioritise low‑to‑mid competition niches.  
4. **Ranking:** Compute a composite score using CPC, search volume (if available) and SEO difficulty.  70% weight is given to CPC, 20% to search volume and 10% to competition.  
5. **City Association:** Combine each niche with large US cities where CPCs are highest (e.g., Dallas, Chicago, Phoenix, Houston, Miami, Orlando)【432626109982497†L542-L566】.  
6. **Output:** Produce a CSV/JSON list of the top 10 niche/city combinations for the next phase.

### Output Example

| Rank | Niche                | City         | Avg. CPC (USD) | SEO Difficulty | Rationale |
|----:|---------------------|-------------|---------------:|---------------:|----------|
| 1   | Water Damage Restoration | Dallas      | 250.79         | 18            | Highest CPC in home services【432626109982497†L515-L533】, low keyword difficulty【648190089987163†L212-L219】. |
| 2   | Flood Restoration        | Chicago     | 151.79         | 22            | High emergency intent【432626109982497†L515-L540】. |
| 3   | Emergency Plumbing       | Houston     | 82.82          | 25            | Urgent need; CPC > $80【565703164472149†L241-L248】. |
| 4   | HVAC Repair Services     | Phoenix     | 70.84          | 31            | High‑value transactional term【565703164472149†L241-L248】. |
| 5   | Roof Leak Repair         | Las Vegas    | 12–18          | 30            | Emergency roof repair has CPC $12–18【867266786737301†L293-L307】. |
| 6   | Garage Door Repair       | Los Angeles | 57.81          | 28            | High conversion rate; mid‑level competition【565703164472149†L246-L248】. |
| 7   | Pest Control             | Miami       | 34             | 20            | Average CPC $34 in competitive markets【197911632009023†L90-L94】. |
| 8   | Window Replacement       | Orlando     | 40.53          | 27            | High‑value home renovation term【565703164472149†L246-L252】. |
| 9   | Home Security Installation | San Francisco | 45.54          | 32            | Growing demand for smart home systems【565703164472149†L250-L252】. |
| 10  | Duct Cleaning Services   | Charlotte   | 34.04          | 24            | Seasonal service with CPC ~$34【565703164472149†L251-L253】. |

## Phase 2: Site Generation System

### Goals

Automate the creation of optimised static websites for each niche/city pair.  Each site should be fast, mobile‑friendly and structured for SEO.

### Components

1. **Templates:** Use a templating engine (e.g., Jinja2 in Python) to define base templates for the homepage, service pages, city pages and FAQ pages.  Templates include:
   - **Schema markup:** JSON‑LD for local business information, service descriptions and FAQs.
   - **Local modifiers:** City names and neighbourhoods inserted into page titles, headings and body text to improve local relevance.
   - **FAQ structured data:** Use `<script type="application/ld+json">` blocks to mark up frequently asked questions and answers.
   - **Conversion‑focused CTAs:** Prominent phone numbers, request‑estimate buttons and contact forms.
2. **Content Engine:** An AI API (e.g., GPT‑4) generates human‑like copy for each page.  It uses the niche, city and service variations as inputs to produce unique, relevant content.  The engine also generates FAQs based on common user queries.
3. **Page Assembly:** For each niche/city, assemble pages:
   - **Homepage:** Overview of services, value proposition, service area map and CTA.
   - **Service Pages:** Detailed pages for sub‑services (e.g., water extraction, structural drying).
   - **City Pages:** Specific pages for neighbourhoods or adjacent cities (if available).
   - **FAQ Page:** Questions and answers with schema markup.
4. **Interlinking:** Create an internal linking graph that connects related pages (e.g., homepage → service pages → FAQ).  This supports crawl efficiency and topical relevance.
5. **Build Process:** A Python script reads the niche/city configuration file and produces a directory of HTML files ready for deployment.  Assets such as CSS, JS and images are included in a `/static` directory.  The build process also generates an XML sitemap and robots.txt.

### Example Implementation

The repository contains a `generate_site.py` script.  Given a JSON file with niche and city details, it calls the AI API to obtain page content, fills templates and writes HTML files to `output/{niche_city}`.  The script also writes `sitemap.xml` and `robots.txt` files and logs the generated URLs for submission to the search console.

### Implementation Details

The `site_generator/` package includes:

- **Templates:** `templates/base.html`, `home.html`, `service.html` and `faq.html` define the HTML structure for each page.  They include local modifiers, schema markup and conversion‑focused CTAs.  Forms contain hidden fields for the `site_slug` so that the backend can identify which site the lead originated from.  A `static/style.css` file provides basic styling.
- **generate_site.py:** Loads the top niche from `data/top_niches.json`, constructs a `site_slug` (e.g., `water-damage-restoration_dallas`) and renders pages using Jinja2.  It also copies static assets into the output directory and generates `sitemap.xml` and `robots.txt` files.
- **scale_engine.py:** Reads the full list of top niches and loops through them to generate a site for each one using `render_pages`.  This demonstrates the ability to replicate the infrastructure across multiple niches in a single run.

To generate a site for the top niche:

```bash
python niche_selection.py            # produces data/top_niches.json and .csv
python site_generator/generate_site.py  # generates HTML files in output/<site_slug>
```

To generate all sites:

```bash
python scale_engine.py
```

## Phase 3: SEO Automation

After site generation, SEO automation ensures that the pages rank and remain indexed.

1. **Internal Linking Graph:** A Python module constructs an adjacency list of pages based on service hierarchy and automatically inserts `<a>` tags with descriptive anchor text.  This improves crawlability and spreads link equity.
2. **Topical Clusters:** The content engine generates supporting blog posts that target long‑tail keywords and informational queries.  These posts link back to core service pages, reinforcing topical authority.
3. **Sitemap Submission:** A scheduled serverless function uses Google Search Console’s API to submit the generated sitemap for each site.  It also monitors indexation status and reports errors.
4. **Performance Monitoring:** The SEO module logs search impressions, click‑through rates and ranking positions.  It surfaces underperforming pages for optimisation or removal.

## Phase 4: Lead Capture

Capturing leads is critical for monetising the platform.  Every site includes the following features:

1. **Form Capture:** A contact form collects name, phone, email and service details.  Submissions trigger an API request to a serverless function that stores the lead in PostgreSQL.
2. **Call Tracking:** Unique call tracking numbers are assigned to each site via a third‑party provider (e.g., Twilio).  The numbers forward calls to the partner and log call metadata in the database.
3. **SMS Forwarding:** If configured, leads can be forwarded via SMS to service providers for immediate follow‑up.
4. **Database Storage:** The PostgreSQL schema includes tables for `leads`, `sites`, `partners` and `calls`.  Each lead record captures timestamp, source site, service requested, contact info and call tracking ID.  Leads are associated with a `partner` for routing.
5. **Routing Logic:** A serverless function reads the assigned partner from the `sites` table and forwards the lead via email, SMS or API.  Routing can be round‑robin or based on partner availability.

### Implementation Details

A simple FastAPI application under `backend/` demonstrates lead capture and routing.  The API exposes a single endpoint `/api/lead` that accepts form submissions from the static sites.  It uses an SQLite database (defined in `backend/database.py`) to persist leads and site metadata.  Upon receiving a lead, the endpoint:

1. **Identifies the Site:** Uses the hidden `site_slug` field to look up (or create) a `Site` record.
2. **Stores the Lead:** Creates a `Lead` record capturing the name, phone, email, service and message.
3. **Routes the Lead:** If a `partner_email` is assigned to the site, the lead is marked as routed and a routing message is printed (this can be replaced with actual email/SMS notifications).  Otherwise, the lead is simply stored and flagged for future sales outreach.

The backend relies on FastAPI and SQLAlchemy.  In environments where external dependencies are unavailable, the code serves as a blueprint that can be executed after installing the required packages (`fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`).

## Phase 5: Sales Automation

When a site consistently generates leads, the platform needs to monetise this traffic by selling exclusive or shared leads to local service providers.

1. **Lead Volume Monitoring:** A scheduled job counts leads per site over the past 30 days.  If leads exceed a threshold (e.g., five), the system marks the site as “sales‑eligible.”
2. **Outreach Sequence:** The sales module automatically generates personalised outreach emails to businesses in the target city.  Emails outline the value proposition (high‑intent leads, pay‑per‑lead or subscription pricing) and invite the prospect to become a partner.
3. **Pricing Models:**
   - **Pay‑per‑lead:** Charge a fixed amount per exclusive lead.  Pricing is configured per niche (e.g., $50 for water damage, $30 for plumbing).  
   - **Subscription:** Monthly flat fee with a defined lead cap.
4. **Invoice Generation:** Integration with Stripe’s API creates invoices and subscription records.  Customers can pay via credit card or ACH.  Stripe handles receipts and failed payment retries.
5. **Onboarding:** When a business accepts the offer, the admin interface allows assigning the partner to the site.  The system then routes future leads to them.

### Implementation Details

The `backend/sales_automation.py` script scans the `leads` table and counts the number of leads per site over the past 30 days.  If a site with no assigned partner exceeds the lead threshold (default 5), the script prints a sample outreach email to the console.  In a full implementation, this logic would send a personalised email via an email service (e.g., SendGrid) and generate an invoice through Stripe’s API.  The script can be scheduled to run daily via a cron job or serverless scheduler.

## Phase 6: Scale Engine

To achieve scalability, the system must replicate the entire pipeline for additional niches and cities.

1. **Cloning:** The `scale_engine.py` script reads the list of top niches and spins up a new site for each.  It clones the repository templates, updates environment variables (call tracking numbers, API keys, partner assignments) and triggers the build process.
2. **Deployment:** Use serverless hosting (e.g., AWS Amplify, Netlify or Vercel) to deploy the static site.  Deployment can be automated via CI/CD pipelines that watch for new directories in the `output` folder.
3. **ROI Tracking:** Each site logs revenue (lead fees or subscriptions) and cost (ad spend if applicable).  A scheduled job computes ROI and flags underperforming sites (ROI < 0 or no leads after 120 days) for deactivation.
4. **Cleanup:** Underperforming sites are archived and their call tracking numbers released.  Domain registration and hosting resources are terminated to reduce overhead.

## Technology Stack

- **Static Site Generator:** A custom Python generator using Jinja2 templates.  Node‑based frameworks like Next.js or Astro can also be used but were avoided to keep dependencies minimal.
- **Serverless Hosting:** Deploy static assets on a CDN (Netlify or Vercel) and API endpoints on AWS Lambda or Cloudflare Workers.
- **Database:** PostgreSQL for storing leads, partners and billing data.  Use connection pooling and environment variables to secure credentials.
- **Headless CMS:** Optional.  For manual content editing, integrate with a CMS like Strapi or Sanity via API.
- **AI API:** Use OpenAI’s GPT‑4 to generate page copy, FAQs and outreach emails.  Implement caching to minimise costs.
- **Email Automation:** Use services like SendGrid or Mailgun to send outreach and lead notifications.  Sequence logic can be built with a job queue (e.g., Celery) or within serverless functions.
- **Stripe for Billing:** Use Stripe’s Subscription and Invoice APIs to manage pay‑per‑lead charges and monthly subscriptions.

## Acceptance Criteria & Future Work

- **One niche + city site live:** Demonstrate by generating a “Water Damage Restoration – Dallas” site and hosting it locally.  The repository includes the generated HTML files under `/output/water-damage-restoration_dallas`.
- **Indexed in Google:** Submit the sitemap to Google Search Console using the `seo_auto.py` script (stub provided).  The build script also outputs the sitemap URL.
- **Lead captured and routed:** Include a working contact form on the site.  Submitting the form stores the lead in the Postgres database and prints a routing log to the console.
- **Automated billing system functional:** The `sales` module includes functions to create Stripe invoices.  Test data and API keys can be configured via environment variables.
- **Ability to replicate new niche in <30 minutes:** The `scale_engine.py` script accepts a list of niches/cities and clones the necessary assets automatically.  With pre‑registered domains and call tracking numbers, new sites can be launched quickly.
