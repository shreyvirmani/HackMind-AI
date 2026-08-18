from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.routes.workflow import router as workflow_router
from api.routes.projects import router as projects_router
from api.routes.chat import router as chat_router
from api.routes.subscription import router as subscription_router
from api.routes.payments import router as payments_router
from api.routes.ideas import router as ideas_router

from database.connection import engine, Base
from database import models
from database.migrations import run_startup_migrations

from websocket_manager import manager


app = FastAPI(
    title="HackMind AI API",
    version="1.0.0",
)


# ===========================
# Create database tables
# ===========================

Base.metadata.create_all(bind=engine)

# Additive, idempotent column migrations for existing tables --
# create_all() above only creates missing tables, it never alters
# columns on ones that already exist. Safe to run on every startup.
run_startup_migrations(engine)


# ===========================
# CORS Configuration
# ===========================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "https://hackmind-ai-copilot.vercel.app",
    ],

    allow_origin_regex=r"https://.*\.vercel\.app",

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# ===========================
# API Routes
# ===========================

app.include_router(workflow_router)
app.include_router(projects_router)
app.include_router(chat_router)
app.include_router(subscription_router)
app.include_router(payments_router)
app.include_router(ideas_router)


# ===========================
# WebSocket Endpoint
# ===========================

@app.websocket("/ws/workflow/{workflow_id}")
async def workflow_socket(
    websocket: WebSocket,
    workflow_id: str,
):

    await manager.connect(
        workflow_id,
        websocket,
    )

    try:

        while True:

            # Receive heartbeat messages
            # from frontend to keep socket alive
            await websocket.receive_text()


    except WebSocketDisconnect:

        manager.disconnect(
            workflow_id,
            websocket,
        )


    except Exception:

        manager.disconnect(
            workflow_id,
            websocket,
        )


# ===========================
# Root Endpoint
# ===========================

@app.get("/")
def root():

    return {
        "message": "HackMind AI API is running 🚀"
    }
