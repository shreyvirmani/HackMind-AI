from src.agents.planner import PlannerAgent
from src.parsers.roadmap_parser import parse_roadmap


class PlannerController:

    def __init__(self):
        self.agent = PlannerAgent()

    def generate_plan(self, idea: str):
        response = self.agent.run(idea)
        return parse_roadmap(response)

planner_controller = PlannerController()