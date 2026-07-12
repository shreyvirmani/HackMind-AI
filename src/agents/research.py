from src.agents.base_agent import BaseAgent


class ResearchAgent(BaseAgent):

    from src.prompts.research_prompt import RESEARCH_PROMPT

    @property
    def system_prompt(self):

        return self.RESEARCH_PROMPT