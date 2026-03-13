from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.briefing import Briefing
from app.schemas.briefing import BriefingCreate

def create_briefing(db: Session, payload: BriefingCreate):
    # Just creating the base record for the first pass
    db_briefing = Briefing(
        company_name=payload.companyName,
        ticker=payload.ticker,
        sector=payload.sector,
        analyst_name=payload.analystName,
        summary=payload.summary,
        recommendation=payload.recommendation,
        points=[],
        risks=[],
        metrics=[]
    )
    
    # TODO: Add logic for BriefingPoint, BriefingRisk, and BriefingMetric relationships
    
    db.add(db_briefing)
    db.commit()
    db.refresh(db_briefing)
    return db_briefing

def get_briefing(db: Session, briefing_id: int):
    briefing = db.get(Briefing, briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
    return briefing

def list_briefings(db: Session):
    return db.query(Briefing).all()

def mark_briefing_generated(db: Session, briefing: Briefing, html_content: str):
    # TODO: Update status and save HTML string
    pass

def format_briefing_for_report(briefing: Briefing):
    # TODO: Map ORM to dictionary for Jinja2 template
    return {"id": briefing.id}