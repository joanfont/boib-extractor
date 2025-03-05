
from abc import ABC, abstractmethod

from boib.models import Article, Bulletin, Date, Section


class BulletinExtractor(ABC):

    @abstractmethod
    def extract(self, date: Date) -> list[Bulletin]:
        pass


class SectionExtractor(ABC): 
    
    @abstractmethod
    def extract(self, bulletin: Bulletin) -> list[Section]:
        pass


class ArticleExtractor:
    
    @abstractmethod
    def extract(self, section: Section) -> list[Article]:
        pass