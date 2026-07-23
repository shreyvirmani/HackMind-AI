from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WorkflowState:
    workflow_id: str

    user_id: str

    idea: str

    project_id: Optional[str] = None

    planner: str = "waiting"

    research: str = "waiting"

    judge: str = "waiting"

    pitch: str = "waiting"

    finished: bool = False

    error: Optional[str] = None