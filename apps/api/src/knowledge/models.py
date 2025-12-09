"""Data models for book analysis."""

from pydantic import BaseModel


class Chapter(BaseModel):
    """Chapter structure."""
    index: int
    title: str
    start: int
    end: int


class ChapterAnalysis(BaseModel):
    """Chapter analysis result."""
    chapter_index: int
    title: str
    summary: str
    characters: list[str] = []
    events: list[str] = []
    sentiment: str = ""
    keywords: list[str] = []


class Character(BaseModel):
    """Character model."""
    id: str
    name: str
    aliases: list[str] = []
    description: str = ""
    first_appearance: int = 0
    role: str = "minor"  # protagonist/antagonist/supporting/minor
    attributes: dict = {}


class Event(BaseModel):
    """Event/plot point model."""
    id: str
    chapter: int
    title: str
    summary: str
    characters: list[str] = []
    location: str = ""
    importance: int = 1  # 1-5
    tags: list[str] = []


class Relation(BaseModel):
    """Character relationship."""
    source: str
    target: str
    type: str  # friend/enemy/lover/family/mentor/...
    description: str = ""
    evidence: list[str] = []
    chapters: list[int] = []
