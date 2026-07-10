from src.agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):

    from src.prompts.planner_prompt import PLANNER_PROMPT
    @property
    def system_prompt(self):
        return self.PLANNER_PROMPT