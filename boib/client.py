from datetime import date
import re

from bs4 import BeautifulSoup
import requests


from boib.factories import BulletinTypeFactory
from boib.models import Bulletin
from boib.utils import month_to_number

class Client:
    __BASE_DOMAIN = 'https://www.caib.es'
    __BASE_URL = f'{__BASE_DOMAIN}/eboibfront'

    def __init__(self):
        pass

    def fetch_year(self, year: int) -> list[Bulletin]:
        yearly_calendar_url = f'{self.__BASE_URL}/calendariAnual.do?lang=ca&p_any={year}'
        response = requests.get(yearly_calendar_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        base_date = date(year, 1, 1)

        bulletins = []
    
        table_containers = soup.find_all('div', {'class': 'calendario_anual_mes'})
        for table_container in table_containers:
            month_bulletins = self.__extract_month_bulletins(table_container, base_date)
            bulletins.extend(month_bulletins)
        
        return bulletins

    def __extract_month_bulletins(self, table_container, base_date: date) -> list[Bulletin]:
        bulletins = []
        
        month_str = table_container.find('h3').text
        month = month_to_number(month_str)

        bulletin_divs = table_container.find_all('div', {'class': 'boib'})
        for bulletin_div in bulletin_divs:
            anchor = bulletin_div.find('a')
            bulletin_type = BulletinTypeFactory.from_anchor_class(anchor['class'])
            day = re.match(r'\d+', anchor.text).group(0)

            bulletin_date = base_date.replace(month=month, day=int(day))

            bulletin = Bulletin(
                type=bulletin_type, 
                date=bulletin_date, 
                url=f'{self.__BASE_DOMAIN}/{anchor['href']}', 
                sections=[]
            )

            bulletins.append(bulletin)

        return bulletins