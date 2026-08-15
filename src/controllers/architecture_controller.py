from src.agents.architecture import ArchitectureAgent
from src.parsers.architecture_parser import parse_architecture
from src.models.architecture import ArchitectureReport


class ArchitectureController:
    def __init__(self):
        self.agent = ArchitectureAgent()

    def generate_architecture(self, roadmap_text: str, research_text: str) -> ArchitectureReport:
        response = self.agent.run_from_context(roadmap_text, research_text)
        return parse_architecture(response)


architecture_controller = ArchitectureController()
