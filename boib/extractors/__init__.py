from abc import ABC, abstractmethod

from boib.models import Article, Bulletin, Section


class BulletinExtractor(ABC):

    @abstractmethod
    def extract_year(self, year: int) -> list[Bulletin]:
        pass

    @abstractmethod
    def extract_year_and_month(self, year: int, month: int) -> list[Bulletin]:
        pass


class SectionExtractor(ABC): 
    
    @abstractmethod
    def extract(self, bulletin: Bulletin) -> list[Section]:
        pass


class ArticleExtractor:
    
    @abstractmethod
    def extract(self, section: Section) -> list[Article]:
        pass