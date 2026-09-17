from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, SessionLocal, engine
from app.core.handlers import register_exception_handlers
from app.interviews import models  # noqa: F401
from app.interviews.router import router as interviews_router
from app.questions import models  # noqa: F401
from app.questions.service import seed_if_empty as seed_questions
from app.reports import models  # noqa: F401
from app.reports.router import router as reports_router
from app.templates import models  # noqa: F401
from app.templates.router import router as templates_router
from app.templates.service import seed_if_empty as seed_templates
from app.users import models  # noqa: F401
from app.users.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_questions(db)
        seed_templates(db)
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(templates_router)
    app.include_router(interviews_router)
    app.include_router(reports_router)
    return app


app = create_app()
