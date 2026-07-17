from pydantic import BaseModel


class WorkflowRequest(BaseModel):
    idea: str


class WorkflowResponse(BaseModel):
    roadmap: dict
    research: dict
    judge: dict
    pitch_deck: dict