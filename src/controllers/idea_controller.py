from src.agents.idea_generator import idea_generator_agent
from src.parsers.idea_parser import parse_ideas
from src.models.idea import IdeaResponse


class IdeaController:
    def generate(self, context: str) -> IdeaResponse:
        return parse_ideas(idea_generator_agent.run(context))


idea_controller = IdeaController()
