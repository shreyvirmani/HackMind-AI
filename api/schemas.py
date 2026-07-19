from pydantic import BaseModel


class WorkflowRequest(BaseModel):
    idea: str
    user_id: str


class WorkflowResponse(BaseModel):
    project_id: str
    project_title: str
    description: str
    planner: dict
    research: dict
    judge: dict
    pitch: dict