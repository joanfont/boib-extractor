import os
import logging
import aiofiles

from boib.downloaders import Downloader
from boib.models import Bulletin
from boib.downloaders.utils import (
    fetch_content, 
    get_article_url,
    get_download_path, 
    get_safe_filename, 
)

logger = logging.getLogger(__name__)


class LocalDownloader(Downloader):
    
    def __init__(self, base_dir: str):
        self.__base_dir = base_dir

    async def download(self, bulletin: Bulletin) -> None:
        for section in bulletin.sections:
            for article in section.articles:
                url, url_type = get_article_url(article)

                content = await fetch_content(url)
                local_path = self._get_article_local_path(bulletin, url, url_type)
                
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                async with aiofiles.open(local_path, 'wb') as f:
                    await f.write(content)

    def _get_article_local_path(self, bulletin, url, url_type):
            filename = get_safe_filename(url, url_type)
            
            date_path = get_download_path(bulletin)
            
            return os.path.join(self.__base_dir, date_path, filename)