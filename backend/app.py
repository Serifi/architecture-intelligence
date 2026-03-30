from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.database import Base, engine
from backend.features.project.controller import router as project_router
from backend.features.architecture_decision.controller import router as architecture_decision_router
from backend.features.architecture_decision.status.controller import router as status_router
from backend.features.documentation_template.controller import router as template_router
from backend.features.architecture_decision.history.controller import router as decision_history_router
from backend.features.user.controller import router as user_router
from backend.features.project.attachment.controller import router as project_attachment_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Architecture Intelligence API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=".*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project_router)
app.include_router(architecture_decision_router)
app.include_router(status_router)
app.include_router(template_router)
app.include_router(decision_history_router)
app.include_router(user_router)
app.include_router(project_attachment_router)