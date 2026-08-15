from src.agents.base_agent import BaseAgent
from src.prompts.architecture_prompt import ARCHITECTURE_PROMPT


class ArchitectureAgent(BaseAgent):
    @property
    def system_prompt(self):
        return ARCHITECTURE_PROMPT

    def run_from_context(self, roadmap: str, research: str) -> str:
        # The system prompt includes a literal JSON schema.  Use explicit
        # placeholder replacement instead of str.format so its JSON braces
        # are not interpreted as format fields.
        prompt = (
            self.system_prompt
            .replace("{roadmap}", roadmap)
            .replace("{research}", research)
        )
        return self.llm.generate(
            __import__("src.models.llm_request", fromlist=["LLMRequest"]).LLMRequest(
                prompt=prompt,
                priority="high",
                cache_enabled=True,
            )
        ).content
