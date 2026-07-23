from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.workflow import router as workflow_router
from api.routes.projects import router as projects_router
from api.routes.chat import router as chat_router

from database.connection import engine, Base
from database import models

app = FastAPI(
    title="HackMind AI API",
    version="1.0.0",
)

# Create database tables
Base.metadata.create_all(bind=engine)

# CORS
origins = [
    "http://localhost:3000",
    "https://hackmind-ai-copilot.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(workflow_router)
app.include_router(projects_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "HackMind AI API is running 🚀"}