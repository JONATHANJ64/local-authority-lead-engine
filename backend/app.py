"""FastAPI application for lead capture and routing.

This module exposes a single endpoint `/api/lead` that accepts form data
from the generated static sites.  The endpoint stores the lead in the
database and attempts to route it to the assigned partner (if any).  In
production, additional endpoints and security measures should be
implemented (e.g., validation, rate limiting and CORS settings).
"""
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import SessionLocal, init_db, Site, Lead


app = FastAPI(title="Local Authority Lead Engine API")

# Allow CORS from any origin for demo purposes. In production, restrict this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LeadResponse(BaseModel):
    message: str


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup() -> None:
    """Initialize database tables."""
    init_db()


@app.post("/api/lead", response_model=LeadResponse)
def create_lead(
    site_slug: str = Form(...),
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(None),
    service: str = Form(None),
    message: str = Form(None),
):
    """
    Accept a lead submission from a static site.

    Parameters are submitted via form fields.  If the referenced site
    does not exist in the database, it will be created automatically
    with no assigned partner.
    """
    if not name.strip() or not phone.strip():
        raise HTTPException(status_code=400, detail="Name and phone are required.")

    db: Session = next(get_db())
    # Find or create site entry
    site = db.query(Site).filter_by(slug=site_slug).first()
    if not site:
        # Without context, set niche and city to slug components
        try:
            niche_part, city_part = site_slug.split("_")
            niche = niche_part.replace("-", " ").title()
            city = city_part.replace("-", " ").title()
        except ValueError:
            niche = site_slug
            city = "Unknown"
        site = Site(slug=site_slug, niche=niche, city=city, partner_email=None)
        db.add(site)
        db.commit()
        db.refresh(site)

    # Create new lead record
    lead = Lead(
        site_id=site.id,
        name=name,
        phone=phone,
        email=email,
        service=service,
        message=message,
        routed=False,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Routing logic: if partner assigned, mark as routed and print message
    if site.partner_email:
        lead.routed = True
        db.commit()
        print(f"Routed lead {lead.id} to partner {site.partner_email} for site {site.slug}")
        return {"message": "Thank you! Your request has been routed to our local partner."}
    else:
        print(f"Lead {lead.id} received for site {site.slug}. No partner assigned.")
        return {"message": "Thank you for contacting us. We will reach out shortly."}
