from src.agents.base_agent import BaseAgent
from src.parsers.pitch_deck_parser import parse_pitch_deck
from src.prompts.pitch_deck_prompt import PITCH_DECK_PROMPT
from src.utils.logger import logger


class PitchDeckAgent(BaseAgent):

    @property
    def system_prompt(self) -> str:
        return PITCH_DECK_PROMPT

    def run(self, roadmap_text: str):

        logger.info("PitchDeckAgent started")

        response = super().run(roadmap_text)

        deck = parse_pitch_deck(response)

        logger.info("PitchDeckAgent completed")

        return deck