from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict


@dataclass
class Date: 
    year: int
    month: int | None
    day: int | None

    def as_date(self):
        return date(self.year, self.month, self.day)


class BulletinType: 
    ORDINARY = 'ORDINARY'
    EXTRAORDINARY = 'EXTRAORDINARY'


class URLType:
    PDF = 'PDF'
    HTML = 'HTML'


class SectionType(Enum):
    LEGACY = 'LEGACY'
    
    # New sections
    GENERAL = 'GENERAL'
    PERSONNEL = 'PERSONNEL'
    OTHERS = 'OTHERS'
    ANNOUNCEMENTS = 'ANNOUNCEMENTS'


@dataclass
class Article:
    number: int | None
    organization: str | None
    summary: str | None
    urls: Dict[URLType, str]


@dataclass
class Section:  
    type: SectionType
    url: str
    articles: list[Article]


@dataclass
class Bulletin:
    number: int
    type: BulletinType
    date: date
    url: str
    sections: list[Section]
