from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.deps import get_db
from app.core.schemas import ApiResponse
from app.templates import service
from app.templates.schemas import TemplateOut

router = APIRouter(prefix="/api", tags=["templates"])


@router.get("/templates")
def list_templates(db: DbSession = Depends(get_db)):
    templates = service.list_templates(db)
    data = [TemplateOut.model_validate(t).model_dump() for t in templates]
    return ApiResponse(data=data)
