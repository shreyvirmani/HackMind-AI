from src.agents.research import ResearchAgent
from src.parsers.research_parser import parse_research
from src.models.research import ResearchReport


class ResearchController:

    def __init__(self):
        self.agent = ResearchAgent()

    def generate_research(
        self,
        roadmap_text: str,
    ) -> ResearchReport:

        response = self.agent.run(roadmap_text)

        return parse_research(response)


research_controller = ResearchController()