from src.agents.base_agent import BaseAgent
from src.parsers.pitch_deck_parser import parse_pitch_deck
from src.prompts.pitch_deck_prompt import PITCH_DECK_PROMPT


class PitchDeckAgent(BaseAgent):

    @property
    def system_prompt(self) -> str:
        return PITCH_DECK_PROMPT

    def run(self, roadmap_text: str):

        response = super().run(roadmap_text)

        return parse_pitch_deck(response)