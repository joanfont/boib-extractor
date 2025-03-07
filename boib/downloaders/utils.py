import logging
import os
from typing import Tuple, Optional

import httpx

from boib.models import Bulletin, URLType, Section, Article


async def fetch_content(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content


def get_article_url(article: Article) -> Tuple[Optional[str], Optional[URLType]]:
    if URLType.HTML in article.urls:
        return article.urls[URLType.HTML], URLType.HTML
    elif URLType.PDF in article.urls:
        return article.urls[URLType.PDF], URLType.PDF
    return None, None


def get_safe_filename(url: str, url_type: URLType) -> str:
    page = os.path.basename(url).split('?')[0]
    
    if url_type == URLType.HTML:
        return f'{page}.html'
    elif url_type == URLType.PDF:
        return f'{page}.pdf'
    
    return page

def get_download_path(bulletin: Bulletin) -> str:
    path_parts = [
        str(bulletin.date.year),
        f'{bulletin.date.month:02d}',
        f'{bulletin.date.day:02d}'
    ]

    return os.path.join(*path_parts) 