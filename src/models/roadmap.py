from pydantic import BaseModel
from typing import List


class TeamRole(BaseModel):
    role: str
    responsibilities: str


class DevelopmentPhase(BaseModel):
    phase: str
    tasks: List[str]


class TechStack(BaseModel):
    frontend: List[str]
    backend: List[str]
    ai_ml: List[str]
    database: List[str]
    deployment: List[str]


class Roadmap(BaseModel):
    project_title: str
    problem_statement: str
    solution: str

    key_features: List[str]

    tech_stack: TechStack

    system_architecture: str

    development_timeline: List[DevelopmentPhase]

    team_roles: List[TeamRole]

    future_scope: str