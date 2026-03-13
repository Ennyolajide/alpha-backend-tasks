from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.briefing import Briefing, BriefingPoint, BriefingRisk, BriefingMetric
from app.schemas.briefing import BriefingCreate

def create_briefing(db: Session, payload: BriefingCreate) -> Briefing:
    # 1. Start with the parent record
    db_briefing = Briefing(
        company_name=payload.companyName,
        ticker=payload.ticker,
        sector=payload.sector,
        analyst_name=payload.analystName,
        summary=payload.summary,
        recommendation=payload.recommendation,
        status='draft'
    )
    db.add(db_briefing)
    
    # 2. We flush to generate the ID without closing the transaction. 
    # This lets us link child records (FKs) before we actually commit.
    db.flush() 

    # 3. Handle related tables. Using enumerate for 'display_order' 
    # ensures the frontend can sort them exactly as they were entered.
    for i, content in enumerate(payload.keyPoints):
        db.add(BriefingPoint(briefing_id=db_briefing.id, content=content, display_order=i))

    for i, content in enumerate(payload.risks):
        db.add(BriefingRisk(briefing_id=db_briefing.id, content=content, display_order=i))

    if payload.metrics:
        for i, m in enumerate(payload.metrics):
            db.add(BriefingMetric(briefing_id=db_briefing.id, name=m.name, value=m.value, display_order=i))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Custom error for the UniqueConstraint on metric names
        raise HTTPException(status_code=400, detail="Metric names must be unique")
    
    db.refresh(db_briefing)
    return db_briefing

def get_briefing(db: Session, briefing_id: int) -> Briefing:
    briefing = db.get(Briefing, briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
    return briefing

def list_briefings(db: Session) -> list[Briefing]:
    return db.query(Briefing).all()

def mark_briefing_generated(db: Session, briefing: Briefing, html_content: str) -> Briefing:
    # We store the final HTML as a string to avoid re-rendering expensive templates later
    briefing.status = 'generated'
    briefing.html_content = html_content
    db.commit()
    db.refresh(briefing)
    return briefing

def format_briefing_for_report(briefing: Briefing) -> dict:
    # Decoupling the DB model from the Template view. 
    # This makes the Jinja2 template much cleaner.
    return {
        "title": f"Internal Briefing Report: {briefing.company_name} ({briefing.ticker})",
        "company_name": briefing.company_name,
        "ticker": briefing.ticker,
        "sector": briefing.sector,
        "analyst_name": briefing.analyst_name,
        "summary": briefing.summary,
        "recommendation": briefing.recommendation,
        "key_points": [p.content for p in briefing.points],
        "risks": [r.content for r in briefing.risks],
        # Title case metrics for better visual presentation
        "metrics": [{"name": m.name.title(), "value": m.value} for m in briefing.metrics],
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }