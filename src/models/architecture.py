from pydantic import BaseModel, Field
from typing import List


class ArchitectureComponent(BaseModel):
    name: str
    type: str
    responsibility: str
    technology: str


class ArchitectureFlow(BaseModel):
    step: int
    from_component: str
    to_component: str
    data: str


class APIContract(BaseModel):
    method: str
    path: str
    purpose: str
    request: str
    response: str


class DatabaseEntity(BaseModel):
    name: str
    purpose: str
    key_fields: List[str] = Field(default_factory=list)


class ArchitectureReport(BaseModel):
    architecture_overview: str
    architectural_pattern: str
    components: List[ArchitectureComponent] = Field(default_factory=list)
    data_flow: List[ArchitectureFlow] = Field(default_factory=list)
    api_contracts: List[APIContract] = Field(default_factory=list)
    database_design: List[DatabaseEntity] = Field(default_factory=list)
    authentication_and_security: List[str] = Field(default_factory=list)
    scalability: List[str] = Field(default_factory=list)
    deployment: List[str] = Field(default_factory=list)
    folder_structure: List[str] = Field(default_factory=list)
    implementation_order: List[str] = Field(default_factory=list)
    key_architecture_decisions: List[str] = Field(default_factory=list)
    mermaid_diagram: str = ""
