import os
from typing import Optional

import aioboto3

from boib.downloaders import Downloader
from boib.models import Bulletin, URLType
from boib.downloaders.utils import (
    fetch_content, 
    get_article_url, 
    get_safe_filename,
    get_download_path
)


class S3Downloader(Downloader):

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region_name: str | None = None,
        endpoint_url: str | None = None,
        prefix: str = '',
    ):
        self.__bucket_name = bucket_name
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__region_name = region_name
        self.__endpoint_url = endpoint_url
        self.__prefix = prefix.rstrip('/') + '/' if prefix else ''

    async def download(self, bulletin: Bulletin) -> None:
        session = aioboto3.Session(
            aws_access_key_id=self.__aws_access_key_id,
            aws_secret_access_key=self.__aws_secret_access_key,
            region_name=self.__region_name,
        )
        
        async with session.client('s3', endpoint_url=self.__endpoint_url) as s3:
            for section in bulletin.sections:
                for article in section.articles:
                    url, url_type = get_article_url(article)
                    
                    if not url:
                        continue
                    
                    try:
                        content = await fetch_content(url)
                        s3_key = self.__get_s3_key(bulletin, url, url_type)
                        
                        await s3.put_object(
                            Bucket=self.__bucket_name,
                            Key=s3_key,
                            Body=content,
                        )
                        
                    except Exception:
                        pass

    def __get_s3_key(self, bulletin: Bulletin, url: str, url_type: URLType) -> str:
        filename = get_safe_filename(url, url_type)
        
        download_path = get_download_path(bulletin)
        
        return os.path.join(self.__prefix, download_path, filename)