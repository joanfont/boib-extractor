import os
import uuid

from httpx import HTTPStatusError

from boib.downloaders import ArticleDownloader, DocumentNotAvailableError, URLNotAvailableError
from boib.filesystems import Filesystem
from boib.models import Article, Bulletin, URLType
from boib.utils import get_async_client


class PDFArticleDownloader(ArticleDownloader):

    def __init__(self, filesystem: Filesystem):
        self.__filesystem = filesystem
    
    async def download(self, bulletin: Bulletin, article: Article):
        path = self.__get_path(bulletin, article)
        content = await self.__get_content(article)

        await self.__filesystem.write(path, content)

    async def __get_content(self, article: Article):
        article_url = article.urls.get(URLType.PDF, None)
        if article_url is None:
            raise URLNotAvailableError()


        async with get_async_client() as client:
            response = await client.get(article_url)

            try:
                response.raise_for_status()
            except HTTPStatusError as e:
                raise DocumentNotAvailableError() from e

            return response.content

    def __get_path(self, bulletin: Bulletin, article: Article) -> str:
        return os.path.join(
            str(bulletin.date.year),
            str(bulletin.date.month),
            str(bulletin.date.day),
            str(bulletin.number),
            f'{article.number or uuid.uuid4()}.pdf'
        )