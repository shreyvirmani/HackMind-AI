from src.agents.base_agent import BaseAgent
from src.prompts.idea_prompt import IDEA_PROMPT


class IdeaGeneratorAgent(BaseAgent):
    @property
    def system_prompt(self):
        return IDEA_PROMPT


idea_generator_agent = IdeaGeneratorAgent()
