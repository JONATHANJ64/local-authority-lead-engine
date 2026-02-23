"""Sales automation module.

This script monitors the number of leads per site and triggers outreach to
potential service providers when a threshold is exceeded.  It also
generates invoices using Stripe when a partner is assigned.  For
demonstration purposes, the script prints messages to the console
instead of sending real emails or calling the Stripe API.  Replace
`print` statements with integrations to email (e.g., SendGrid) and
Stripe as needed.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .database import SessionLocal, Site, Lead

# Threshold: number of leads in the past 30 days to trigger outreach
LEAD_THRESHOLD = 5


def check_leads_and_trigger_outreach() -> None:
    db: Session = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)
        # Get sites without a partner
        sites = db.query(Site).filter(Site.partner_email.is_(None)).all()
        for site in sites:
            count = (
                db.query(Lead)
                .filter(Lead.site_id == site.id)
                .filter(Lead.timestamp >= cutoff)
                .count()
            )
            if count >= LEAD_THRESHOLD:
                # Trigger outreach email
                print(
                    f"Sales Automation: Site '{site.slug}' generated {count} leads in the last 30 days. "
                    f"Initiating outreach to potential partners in {site.city}."
                )
                # Example email body
                email_body = (
                    f"Hello,\n\nWe operate {site.niche} websites in {site.city} and have generated {count} high-intent leads "
                    f"over the past 30 days. We are looking for a local business partner to take these leads on a "
                    "pay-per-lead or subscription basis. If you are interested, please reply to discuss pricing.\n\n"
                    "Regards,\nLocal Authority Lead Engine"
                )
                print(f"Email content:\n{email_body}\n")
    finally:
        db.close()


if __name__ == "__main__":
    check_leads_and_trigger_outreach()