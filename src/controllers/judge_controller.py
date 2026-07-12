from src.agents.judge import JudgeAgent


class JudgeController:

    def __init__(self):
        self.agent = JudgeAgent()

    def evaluate_project(self, roadmap_text: str):
        return self.agent.run(roadmap_text)


judge_controller = JudgeController()