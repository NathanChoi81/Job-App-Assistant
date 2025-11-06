"""Type definitions for services"""

from pydantic import BaseModel
from typing import Literal


class Skill(BaseModel):
    """Skill model"""
    name: str
    source: Literal["requirement", "responsibility", "nice_to_have", "static"]
    locked: bool
    score: float | None = None


class CourseworkItem(BaseModel):
    """Coursework item model"""
    name: str
    score: float | None = None


class ParsedResume(BaseModel):
    """Parsed resume structure"""
    sections: dict[str, str]
    technicalSkills: list[Skill]
    relevantCoursework: list[CourseworkItem]


class JDSpan(BaseModel):
    """JD text span with character indices"""
    requirements: list[tuple[int, int]]
    responsibilities: list[tuple[int, int]]
    nice_to_haves: list[tuple[int, int]]

