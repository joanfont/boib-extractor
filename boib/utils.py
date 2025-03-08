from bs4 import BeautifulSoup
import httpx

__HTTPX_CLIENT_OPTIONS = {
    'transport': httpx.AsyncHTTPTransport(local_address='0.0.0.0'),
    'timeout': 3600,
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ca-ES,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    },
    'follow_redirects': True,
}


def month_to_number(month: str): 
    months = [
        'gener',
        'febrer',
        'març',
        'abril',
        'maig',
        'juny',
        'juliol',
        'agost',
        'setembre',
        'octubre',
        'novembre',
        'desembre'
    ]

    return months.index(month) + 1


def get_async_client(**options): 
    client_options = {**__HTTPX_CLIENT_OPTIONS, **options}

    return httpx.AsyncClient(**client_options)


async def get_soup(url: str) -> BeautifulSoup:
    async with get_async_client() as client:
        response = await client.get(url)
        response.raise_for_status()

        return BeautifulSoup(response.text, 'html.parser')


def url_is_absolute(url: str) -> bool:
    return url.startswith('http')