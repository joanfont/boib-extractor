import asyncio
from datetime import date as datetype

import click

from boib.downloaders import BulletinDownloader
from boib.downloaders.composite import CompositeArticleDownloader
from boib.downloaders.html import HTMLArticleDownloader
from boib.downloaders.pdf import PDFArticleDownloader
from boib.extractors.caib import CAIBBulletinExtractor
from boib.filesystems.local import LocalFilesystem
from boib.models import Date


extractor = CAIBBulletinExtractor()

filesystem = LocalFilesystem('/data')
downloader = BulletinDownloader(
    CompositeArticleDownloader([
        HTMLArticleDownloader(filesystem),
        PDFArticleDownloader(filesystem),
    ])
)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('year', type=int)
@click.argument('month', type=int, required=False)
@click.argument('day', type=int, required=False)
def fetch(year, month=None, day=None):
    date = Date(year, month, day)
    bulletins = asyncio.run(extractor.extract(date))

    for bulletin in bulletins:
        asyncio.run(downloader.download(bulletin))


@cli.command()
def today():
    today = datetype.today()
    date = Date(today.year, today.month, today.day)

    bulletins = asyncio.run(extractor.extract(date))

    for bulletin in bulletins:
        asyncio.run(downloader.download(bulletin))

if __name__ == '__main__':
    cli()