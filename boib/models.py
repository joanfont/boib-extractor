from dataclasses import dataclass
from datetime import date
from enum import Enum


class BulletinType: 
    ORDINARY = 'ORDINARY'
    EXTRAORDINARY = 'EXTRAORDINARY'


class SectionType(Enum):
    LEGACY = 'LEGACY'
    
    # New sections
    GENERAL = 'GENERAL'
    PERSONNEL = 'PERSONNEL'
    OTHERS = 'OTHERS'
    ANNOUNCEMENTS = 'ANNOUNCEMENTS'


@dataclass
class Article:
    organization: str | None
    summary: str | None
    url: str


@dataclass
class Section:  
    type: SectionType
    url: str
    articles: list[Article]


@dataclass
class Bulletin:
    type: BulletinType
    date: date
    url: str
    sections: list[Section]
