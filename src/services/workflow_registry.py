from typing import Dict
from src.models.workflow_state import WorkflowState


class WorkflowRegistry:

    def __init__(self):
        self._workflows: Dict[str, WorkflowState] = {}

    def create(self, workflow: WorkflowState):
        self._workflows[workflow.workflow_id] = workflow

    def get(self, workflow_id: str):
        return self._workflows.get(workflow_id)

    def remove(self, workflow_id: str):
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]

    def exists(self, workflow_id: str):
        return workflow_id in self._workflows


workflow_registry = WorkflowRegistry()