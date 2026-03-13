from typing import Annotated
from fastapi import APIRouter, Depends, status, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.briefing import BriefingCreate, BriefingResponse
from app.services import briefing_service as service

router = APIRouter(prefix="/briefings", tags=["briefings"])
templates = Jinja2Templates(directory="app/templates")

@router.post("", response_model=BriefingResponse, status_code=201)
def create_briefing(payload: BriefingCreate, db: Annotated[Session, Depends(get_db)]):
    # takes validated json and hands it to the service for the multi-table save
    return service.create_briefing(db, payload)

@router.get("", response_model=list[BriefingResponse])
def list_briefings(db: Annotated[Session, Depends(get_db)]):
    # returns all briefings; response_model handles the orm-to-json mapping
    return service.list_briefings(db)

@router.get("/{id}", response_model=BriefingResponse)
def get_briefing(id: int, db: Annotated[Session, Depends(get_db)]):
    # standard pk lookup
    return service.get_briefing(db, id)

@router.post("/{id}/generate")
def generate_report(request: Request, id: int, db: Annotated[Session, Depends(get_db)]):
    # pulls raw data, transforms it for the template, and bakes it into 
    # a static html string to be stored in the db.
    briefing = service.get_briefing(db, id)
    view_model = service.format_briefing_for_report(briefing)
    
    template = templates.get_template("report.html")
    html = template.render({"request": request, **view_model})
    
    service.mark_briefing_generated(db, briefing, html)
    return {"message": "Report generated successfully", "status": "generated"}

@router.get("/{id}/html", response_class=HTMLResponse)
def view_html_report(id: int, db: Annotated[Session, Depends(get_db)]):
    # serves the pre-rendered html directly from the db to save on cpu/rendering time
    briefing = service.get_briefing(db, id)
    
    if not briefing.html_content:
        raise HTTPException(status_code=400, detail="Report has not been generated yet")
        
    return HTMLResponse(content=briefing.html_content)