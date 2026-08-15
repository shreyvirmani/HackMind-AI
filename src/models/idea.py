from pydantic import BaseModel, Field
from typing import List


class ProjectIdea(BaseModel):
    title: str
    description: str
    problem: str
    solution: str
    mvp_features: List[str] = Field(default_factory=list)
    tech_direction: List[str] = Field(default_factory=list)


class IdeaResponse(BaseModel):
    ideas: List[ProjectIdea]
