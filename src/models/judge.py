from pydantic import BaseModel
from typing import List


class Score(BaseModel):
    category: str
    score: int
    feedback: str


class JudgeReport(BaseModel):
    overall_score: int

    overall_feedback: str

    strengths: List[str]

    weaknesses: List[str]

    improvements: List[str]

    scores: List[Score]