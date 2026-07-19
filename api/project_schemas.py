from pydantic import BaseModel
from datetime import datetime


class ProjectSummary(BaseModel):
    id: int
    project_title: str
    overall_score: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True