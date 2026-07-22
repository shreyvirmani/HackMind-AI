from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.workflow import router as workflow_router
from database.connection import engine, Base
from database import models
from api.routes.projects import router as projects_router
from api.routes.chat import router as chat_router

app = FastAPI(
    title="HackMind AI API",
    version="1.0.0",
)

Base.metadata.create_all(
    bind=engine
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflow_router)
app.include_router(projects_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "HackMind AI API is running 🚀"
    }