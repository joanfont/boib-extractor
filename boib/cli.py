import click

from boib.extractors.caib import CAIBBulletinExtractor


@click.group()
def cli():
    pass


@cli.command()
@click.argument('year', type=int)
@click.argument('month', type=int, required=False)
def fetch(year, month=None):
    extractor = CAIBBulletinExtractor()
    if month is not None:
        bulletins = extractor.extract_year_and_month(year, month)
        click.echo(f'Found {len(bulletins)} bulletins for date {month}/{year}')
    else: 
        bulletins = extractor.extract_year(year)
        click.echo(f'Found {len(bulletins)} bulletins for year {year}')

    for bulletin in bulletins:
        click.echo(f'Bulletin: {bulletin.date.strftime('%Y-%m-%d')} - {bulletin.type} - {bulletin.url}')
        for section in bulletin.sections: 
            click.echo(f'==== {section.type} =====')
            for article in section.articles:
                click.echo(f'\t * {article.organization} - {article.url}')
            
            click.echo()
        
        click.echo()

if __name__ == '__main__':
    cli()