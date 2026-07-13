from src.agents.pitch_deck import PitchDeckAgent


class PitchDeckController:

    def __init__(self):
        self.agent = PitchDeckAgent()

    def generate_pitch_deck(self, roadmap_text: str):
        return self.agent.run(roadmap_text)


pitch_deck_controller = PitchDeckController()