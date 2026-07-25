from src.agents.planner import PlannerAgent
from src.parsers.roadmap_parser import parse_roadmap


class PlannerController:

    def __init__(self):
        self.agent = PlannerAgent()

    def generate_plan(self, idea: str):
        response = self.agent.run(idea)

        print("=" * 80)
        print("TYPE:", type(response))
        print("RESPONSE:")
        print(response)
        print("=" * 80)

        return parse_roadmap(response)

planner_controller = PlannerController()