from abc import ABC, abstractmethod
import os
import uuid

from boib.filesystems import Filesystem
from boib.models import Article, Bulletin
from boib.log import logger

class ArticleDownloader(ABC):

    @abstractmethod
    async def download(self, bulletin: Bulletin, article: Article):
        pass


class BulletinDownloader:

    def __init__(self, article_downloader: ArticleDownloader):
        self.__article_downloader = article_downloader

    async def download(self, bulletin: Bulletin): 
        logger.info(f'Starting download for bulletin {bulletin.number} ({bulletin.date})')
        for section in bulletin.sections:
            logger.debug(f'Processing section: {section.type}')
            for article in section.articles:
                try:
                    logger.debug(f'Downloading article: {article.number}')
                    await self.__article_downloader.download(bulletin, article)
                except DocumentNotAvailableError as e:
                    logger.warning(f'Document not available for article: {article.number}. Error: {str(e)}')
                    continue
        
        logger.info(f'Completed download for bulletin {bulletin.number} ({bulletin.date})')


class URLNotAvailableError(Exception):
    pass


class DocumentNotAvailableError(Exception):
    pass