from dataclasses import dataclass
from typing import List


@dataclass
class Answer:
    title: str
    is_correct: bool


@dataclass
class Question:
    id: int | None
    title: str
    theme_id: int
    answers: List[Answer]


@dataclass
class Theme:
    id: int | None
    title: str