from abc import ABC, abstractmethod
import os
import uuid

from boib.filesystems import Filesystem
from boib.models import Article, Bulletin

class ArticleDownloader(ABC):

    @abstractmethod
    async def download(self, bulletin: Bulletin, article: Article):
        pass


class BulletinDownloader:

    def __init__(self, article_downloader: ArticleDownloader):
        self.__article_downloader = article_downloader

    async def download(self, bulletin: Bulletin): 
        for section in bulletin.sections:
            for article in section.articles:
                await self.__article_downloader.download(bulletin, article)


class URLNotAvailableError(Exception):
    pass