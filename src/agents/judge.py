from src.agents.base_agent import BaseAgent
from src.parsers.judge_parser import parse_judge
from src.prompts.judge_prompt import JUDGE_PROMPT


class JudgeAgent(BaseAgent):

    @property
    def system_prompt(self) -> str:
        return JUDGE_PROMPT

    def run(self, roadmap_text: str):

        response = super().run(roadmap_text)

        return parse_judge(response)