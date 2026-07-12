from pydantic import BaseModel


class Competitor(BaseModel):
    name: str
    description: str


class ApiSuggestion(BaseModel):
    name: str
    purpose: str


class Risk(BaseModel):
    title: str
    mitigation: str


class ResearchReport(BaseModel):
    competitors: list[Competitor]

    recommended_apis: list[ApiSuggestion]

    implementation_risks: list[Risk]

    deployment_advice: list[str]

    optimization_tips: list[str]