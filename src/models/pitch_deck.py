from pydantic import BaseModel
from typing import List


class Slide(BaseModel):
    title: str
    content: List[str]


class PitchDeck(BaseModel):
    slides: List[Slide]