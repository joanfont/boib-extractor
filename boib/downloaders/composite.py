from boib.downloaders import ArticleDownloader, URLNotAvailableError
from boib.models import Article, Bulletin


class CompositeArticleDownloader(ArticleDownloader):

    def __init__(self, article_downloaders: list[ArticleDownloader]):
        self.__article_downloaders = article_downloaders
    
    async def download(self, bulletin: Bulletin, article: Article):
        for article_downloader in self.__article_downloaders:
            try:
                await article_downloader.download(bulletin, article)
                return
            except URLNotAvailableError: 
                pass