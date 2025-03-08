import os
import uuid

from boib.downloaders import ArticleDownloader, URLNotAvailableError
from boib.filesystems import Filesystem
from boib.models import Article, Bulletin, URLType
from boib.utils import get_soup

class HTMLArticleDownloader(ArticleDownloader):

    def __init__(self, filesystem: Filesystem):
        self.__filesystem = filesystem
    
    async def download(self, bulletin: Bulletin, article: Article):
        path = self.__get_path(bulletin, article)
        content = await self.__get_content(article)

        await self.__filesystem.write(path, bytes(content, 'utf-8'))

    async def __get_content(self, article: Article):
        article_url = article.urls.get(URLType.HTML, None)
        if article_url is None:
            raise URLNotAvailableError()

        soup = await get_soup(article_url)

        content_div = soup.find('div', {'id' : 'contenidoEdicto'})

        return content_div.text

    def __get_path(self, bulletin: Bulletin, article: Article) -> str:
        return os.path.join(
            str(bulletin.date.year),
            str(bulletin.date.month),
            str(bulletin.date.day),
            str(bulletin.number),
            f'{article.number or uuid.uuid4()}.txt'
        )