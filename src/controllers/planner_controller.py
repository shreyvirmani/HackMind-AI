from src.agents.planner import PlannerAgent


class PlannerController:

    def __init__(self):
        self.agent = PlannerAgent()

    def generate_plan(self, idea: str):
        return self.agent.run(idea)


planner_controller = PlannerController()