"""Database models and connection management.

This module defines SQLAlchemy models for the lead engine and creates a
SQLite database for demonstration purposes.  In production, update the
SQLALCHEMY_DATABASE_URL to point to a PostgreSQL instance (e.g.,
`postgresql+psycopg2://user:password@host/dbname`).

The database contains simple tables for Sites and Leads.  Additional
tables such as Partners and Calls can be added as needed.
"""
from datetime import datetime
from sqlalchemy import (create_engine, Column, Integer, String, Text,
                        DateTime, ForeignKey, Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///" + __file__.replace("database.py", "leads.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    niche = Column(String, nullable=False)
    city = Column(String, nullable=False)
    partner_email = Column(String, nullable=True)

    leads = relationship("Lead", back_populates="site")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    service = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    routed = Column(Boolean, default=False)

    site = relationship("Site", back_populates="leads")


def init_db():
    """Create all tables. Call this at application startup."""
    Base.metadata.create_all(bind=engine)