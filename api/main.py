from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.routes.workflow import router as workflow_router
from api.routes.projects import router as projects_router
from api.routes.chat import router as chat_router

from database.connection import engine, Base
from database import models

from websocket_manager import manager



app = FastAPI(
    title="HackMind AI API",
    version="1.0.0",
)



# Create database tables
Base.metadata.create_all(bind=engine)



# ===========================
# CORS Configuration
# ===========================

app.add_middleware(
    CORSMiddleware,

    # Allow localhost + all Vercel deployments
    allow_origin_regex=r"https://.*\.vercel\.app",

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)



# API Routes
app.include_router(workflow_router)
app.include_router(projects_router)
app.include_router(chat_router)



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



@app.get("/")
def root():

    return {
        "message": "HackMind AI API is running 🚀"
    }