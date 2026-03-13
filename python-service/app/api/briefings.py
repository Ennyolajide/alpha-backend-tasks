from typing import Annotated, List
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
    return service.create_briefing(db, payload)

@router.get("", response_model=List[BriefingResponse])
def list_briefings(db: Annotated[Session, Depends(get_db)]):
    return service.list_briefings(db)

@router.get("/{id}", response_model=BriefingResponse)
def get_briefing(id: int, db: Annotated[Session, Depends(get_db)]):
    return service.get_briefing(db, id)

@router.post("/{id}/generate")
def generate_report(request: Request, id: int, db: Annotated[Session, Depends(get_db)]):
    briefing = service.get_briefing(db, id)
    # TODO: Implement Jinja2 rendering logic here
    return {"message": "Report generation logic pending implementation"}

@router.get("/{id}/html", response_class=HTMLResponse)
def get_report_html(id: int, db: Annotated[Session, Depends(get_db)]):
    briefing = service.get_briefing(db, id)
    if not briefing.html_content:
        raise HTTPException(status_code=400, detail="Report not yet generated")
    return HTMLResponse(content=briefing.html_content)