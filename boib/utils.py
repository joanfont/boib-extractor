from bs4 import BeautifulSoup
import requests


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


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()

    return BeautifulSoup(response.text, 'html.parser')


def url_is_absolute(url: str) -> bool:
    return url.startswith('http') or url.startswith('https')