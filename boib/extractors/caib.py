from datetime import date as datetype
import re

from bs4 import BeautifulSoup

from boib.extractors import ArticleExtractor, BulletinExtractor, SectionExtractor
from boib.factories import BulletinTypeFactory, SectionTypeFactory
from boib.models import Article, Bulletin, Date, Section, SectionType, URLType
from boib.utils import get_soup, month_to_number, url_is_absolute
from boib.log import logger


class CAIBBaseExtractor:
    BASE_DOMAIN = 'https://intranet.caib.es'
    BASE_URL = f'{BASE_DOMAIN}/eboibfront'


class CAIBBulletinExtractor(CAIBBaseExtractor, BulletinExtractor):

    def __init__(self,  section_extractor: SectionExtractor = None):
            self.__section_extractor = section_extractor or CAIBSectionExtractor()
        
    async def extract(self, date: Date) -> list[Bulletin]:
        logger.info(f'Starting bulletin extraction')
        yearly_calendar_url = f'{self.BASE_URL}/ca/{date.year}'
        soup = await get_soup(yearly_calendar_url)

        table_containers = soup.find_all('div', {'class': 'calendario_anual_mes'})

        base_date = datetype(date.year, 1, 1)
        if date.month is None:
            logger.debug(f'Extracting all bulletins for year {date.year}')
            bulletins = []
            for table_container in table_containers:
                month_bulletins = await self.__extract_month_bulletins(table_container, base_date)
                bulletins.extend(month_bulletins) 
            
            logger.info(f'Completed extraction of {len(bulletins)} bulletins for year {date.year}')
            return bulletins
        

        base_date = base_date.replace(month=date.month)
        month_table = table_containers[date.month - 1]

        if date.day is None:
            logger.debug(f'Extracting all bulletins for month {date.year}-{date.month}')
            bulletins = await self.__extract_month_bulletins(month_table, base_date)
            logger.info(f'Completed extraction of {len(bulletins)} bulletins for month {date.year}-{date.month}')
            return bulletins

        base_date = base_date.replace(day=date.day)
        day_anchors = month_table.find_all('a', text=re.compile(f'^{date.day}(\\*E)?$'))
        
        logger.debug(f'Extracting bulletins for day {date.year}-{date.month}-{date.day}')
        bulletins = [
            await self.__extract_bulletin(day_anchor, base_date) for day_anchor in day_anchors
        ]
        logger.info(f'Completed extraction of {len(bulletins)} bulletins for day {date.year}-{date.month}-{date.day}')
        return bulletins
    
    async def __extract_month_bulletins(self, table_container, base_date: datetype) -> list[Bulletin]:
        bulletins = []
        
        month_str = table_container.find('h3').text
        month = month_to_number(month_str)
        monthly_date = base_date.replace(month=month)

        bulletin_divs = table_container.find_all('div', {'class': 'boib'})
        logger.debug(f'Found {len(bulletin_divs)} bulletin divs for month {base_date.year}-{month}')
        
        for bulletin_div in bulletin_divs:
            anchors = bulletin_div.find_all('a')
            for anchor in anchors:
                bulletins.append(
                    await self.__extract_bulletin(anchor, monthly_date)
                )

        return bulletins
    
    async def __extract_bulletin(self, anchor_element, base_date):
        bulletin_type = BulletinTypeFactory.from_anchor_class(anchor_element['class'])
        day = re.match(r'\d+', anchor_element.text).group(0)

        bulletin_date = base_date.replace(day=int(day))

        url = f'{self.BASE_DOMAIN}{anchor_element['href']}'
        number = await self.__get_bulletin_number(url)

        logger.debug(f'Extracting bulletin {number} from {bulletin_date}')

        bulletin = Bulletin(
            number=number,
            type=bulletin_type, 
            date=bulletin_date, 
            url=url,
            sections=[]
        )

        bulletin.sections = await self.__section_extractor.extract(bulletin)

        return bulletin

    async def __get_bulletin_number(self, url: str) -> int | None:
        soup = await get_soup(url)
        number_container = soup.find('a', {'class': 'fijo'})
        strong = number_container.find('strong')
        matches = re.findall(r'\d+', strong.text.strip())
        if not matches:
            logger.warning(f'Could not extract bulletin number from {url}')
            return None
        
        return matches[0]


class CAIBSectionExtractor(CAIBBaseExtractor, SectionExtractor):

    def __init__(
        self, 
        article_extractor: ArticleExtractor = None,
    ):
        self.__article_extractor = article_extractor or CAIBArticleExtractor()
        self.__legacy_article_extractor = CAIBLegacyArticleExtractor()

    async def extract(self, bulletin: Bulletin) -> list[Section]:
        logger.debug(f'Extracting sections for bulletin {bulletin.number}')
        soup = await get_soup(bulletin.url)

        sections_list = soup.find('ul', {'class': 'primerosHijos'})
        if sections_list is not None:
           sections = await self.__build_sections(sections_list)
           logger.debug(f'Found {len(sections)} sections for bulletin {bulletin.number}')
           return sections
        elif self.__is_legacy(soup):
            logger.debug(f'Found legacy format for bulletin {bulletin.number}')
            return await self.__build_legacy_sections(bulletin, soup)
    
    async def __build_sections(self, sections_list) -> list[Section]:
        section_items = sections_list.find_all('a', {'rel': 'section'})
        sections = []
        for section_item in section_items:
            section_em = section_item.find('em')
            section_type = SectionTypeFactory.from_section_text(section_em.text)
            
            logger.debug(f'Building section {section_type}')
            section = Section(
                type=section_type,
                url=f'{self.BASE_DOMAIN}{section_item['href']}',
                articles=[]
            )

            section.articles = await self.__article_extractor.extract(section)
            logger.debug(f'Found {len(section.articles)} articles in section {section_type}')

            sections.append(section)
        
        return sections
    
    async def __build_legacy_sections(self, bulletin: Bulletin, soup) -> list[Section]:
        section = Section(
            type=SectionType.LEGACY,
            url=bulletin.url,
            articles=[]
        )

        section.articles = await self.__legacy_article_extractor.extract_from_soup(soup)
        logger.debug(f'Found {len(section.articles)} articles in legacy section')
         
        return [section]

    def __is_legacy(self, soup) -> bool:
        return soup.find('div', {'class': 'caja'})


class CAIBArticleExtractor(CAIBBaseExtractor, ArticleExtractor):

    def __init__(self):
        self.__grouped_article_extractor = CAIBGroupedArticleExtractor()
    
    async def extract(self, section: Section) -> list[Article]:
        logger.debug(f'Extracting articles from section {section.type}')
        soup = await get_soup(section.url)

        if self.__is_grouped(soup):
            logger.debug('Found grouped articles format')
            return await self.__grouped_article_extractor.extract_from_soup(soup)
        else: 
            return await self.__build_articles(soup)
    
    async def __build_articles(self, soup) -> list[Article]:
        articles_list = soup.find('ul', {'class': 'llistat'})
        article_items = articles_list.find_all('div', {'class': 'caja'})

        logger.debug(f'Found {len(article_items)} articles to extract')
        articles = []
        for article_item in article_items:
            registry = article_item.find('p', {'class': 'registre'})
            registry_number = int(re.findall(r'\d+', registry.text)[0])

            organization = article_item.find('h3', {'class': 'organisme'}).text
            summary = article_item.find('ul', {'class': 'resolucions'}).find('p').text
    
            pdf_url_anchor = article_item.find('ul', {'class': 'documents'}).find('a', {'aria-label': 'Exportar a PDF'})
            pdf_url = pdf_url_anchor['href']

            if not url_is_absolute(pdf_url):
                pdf_url = f'{self.BASE_DOMAIN}{pdf_url}'

            html_url_anchor = article_item.find('ul', {'class': 'documents'}).find('a', {'aria-label': 'Exportar a HTML'})
            html_url = html_url_anchor['href']

            if not url_is_absolute(html_url):
                html_url = f'{self.BASE_DOMAIN}{html_url}'
            
            logger.debug(f'Extracted article {registry_number} from {organization}')
            article = Article(
                number=registry_number,
                organization=organization,
                summary=summary,
                urls={
                    URLType.PDF: pdf_url,
                    URLType.HTML: html_url,
                },
            )

            articles.append(article)

        return articles

    def __is_grouped(self, soup) -> bool:
        return soup.find('div', {'class': 'grupoPrincipal'}) is not None


class CAIBGroupedArticleExtractor(CAIBBaseExtractor, ArticleExtractor):
    
    async def extract(self, section: Section) -> list[Article]:
        raise NotImplementedError('Grouped article extraction from section is not supported yet')

    async def extract_from_soup(self, soup: BeautifulSoup) -> list[Article]:
        logger.debug('Starting grouped articles extraction')
        div_container = soup.find('div', {'class': 'grupoPrincipal'})

        ul_items = div_container.find_all('ul', {'class': 'llistat'})
        logger.debug(f'Found {len(ul_items)} article groups')
        
        articles = []
        
        for ul_item in ul_items:
            list_items = ul_item.find_all('li', recursive=False)
            organization_prefix = None

            for list_item in list_items:
                section_heading_item = list_item.find('h3')

                if section_heading_item is not None:
                    organization_prefix = section_heading_item.text

                section_orgs = list_item.find_all('li', recursive=False)
                if section_orgs is None:
                    continue
                
                for section_org in section_orgs:
                    organization_heading_item = section_org.find('h3')
                    organization = organization_prefix
                    if organization_heading_item is not None:
                        organization = f'{organization_prefix} {organization_heading_item.text}'

                    entities_list = section_org.find('ul', {'class': 'entitats'})
                    if entities_list is not None:
                        articles_list = entities_list.find_all('li', recursive=False)

                        for article_item in articles_list:
                            if article_item is not None:
                                registry = article_item.find('p', {'class': 'registre'})
                                if registry is not None:
                                    registry_number = int(re.findall(r'\d+', registry.text)[0])
                                else:
                                    registry_number = None

                                summary = article_item.find('p').text
                                url_anchor = article_item.find('a', {'class': 'pdf'})

                                logger.debug(f'Extracted grouped article {registry_number} from {organization}')
                                article = Article(
                                    number=registry_number,
                                    organization=organization,
                                    summary=summary,
                                    urls={
                                        URLType.PDF: f'{self.BASE_DOMAIN}{url_anchor['href']}',
                                    }
                                )

                                articles.append(article)

        logger.debug(f'Completed extraction of {len(articles)} grouped articles')
        return articles


class CAIBLegacyArticleExtractor(CAIBBaseExtractor, ArticleExtractor):
    
    async def extract(self, section: Section) -> list[Article]:
        raise NotImplementedError('Legacy article extraction from section is not supported yet')

    async def extract_from_soup(self, soup: BeautifulSoup) -> list[Article]:
        logger.debug('Extracting legacy article')
        articles_list = soup.find('ul', {'class': 'llistat'})
        article = articles_list.find('div', {'class': 'caja'})
        url_anchor = article.find('a', {'class': 'pdf'})

        article = Article(
            number=None,
            organization=None,
            summary=None,
            urls={
                URLType.PDF: f'{self.BASE_DOMAIN}{url_anchor['href']}',
            }
        )

        return [article]