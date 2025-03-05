from datetime import date as datetype

import click

from boib.extractors.caib import CAIBBulletinExtractor
from boib.models import Bulletin, Date


extractor = CAIBBulletinExtractor()


def print_bulletins(bulletins: list[Bulletin]):
    for bulletin in bulletins:
        click.echo(f'Bulletin: {bulletin.date.strftime('%Y-%m-%d')} - {bulletin.type} - {bulletin.url}')
        for section in bulletin.sections: 
            click.echo(f'==== {section.type} =====')
            for article in section.articles:
                click.echo(f'\t * {article.organization} - {article.url}')
            
            click.echo()
        
        click.echo()


@click.group()
def cli():
    pass


@cli.command()
@click.argument('year', type=int)
@click.argument('month', type=int, required=False)
@click.argument('day', type=int, required=False)
def fetch(year, month=None, day=None):
    date = Date(year, month, day)

    bulletins = extractor.extract(date)
    print_bulletins(bulletins)


@cli.command()
def today():
    today = datetype.today()
    date = Date(today.year, today.month, today.day)

    bulletins = extractor.extract(date)
    if not bulletins:
        click.echo('No bulletins published today')

    print_bulletins(bulletins)


if __name__ == '__main__':
    cli()