from datetime import date as datetype
import re

from bs4 import BeautifulSoup

from boib.extractors import ArticleExtractor, BulletinExtractor, SectionExtractor
from boib.factories import BulletinTypeFactory, SectionTypeFactory
from boib.models import Article, Bulletin, Date, Section, SectionType
from boib.utils import get_soup, month_to_number, url_is_absolute


class CAIBBaseExtractor:
    BASE_DOMAIN = 'https://www.caib.es'
    BASE_URL = f'{BASE_DOMAIN}/eboibfront'


class CAIBBulletinExtractor(CAIBBaseExtractor, BulletinExtractor):

    def __init__(self,  section_extractor: SectionExtractor = None):
            self.__section_extractor = section_extractor or CAIBSectionExtractor()
        
    def extract(self, date: Date) -> list[Bulletin]:
        yearly_calendar_url = f'{self.BASE_URL}/calendariAnual.do?lang=ca&p_any={date.year}'
        soup = get_soup(yearly_calendar_url)

        table_containers = soup.find_all('div', {'class': 'calendario_anual_mes'})

        base_date = datetype(date.year, 1, 1)
        if date.month is None:
            bulletins = []
            for table_container in table_containers:
                month_bulletins = self.__extract_month_bulletins(table_container, base_date)
                bulletins.extend(month_bulletins) 
            
            return bulletins
        

        base_date = base_date.replace(month=date.month)
        month_table = table_containers[date.month - 1]

        if date.day is None:
            return self.__extract_month_bulletins(month_table, base_date)

        base_date = base_date.replace(day=date.day)
        day_anchors = month_table.find_all('a', text=re.compile(f'^{date.day}(\\*E)?$'))
        

        return [
            self.__extract_bulletin(day_anchor, base_date) for day_anchor in day_anchors
        ]
    
    def __extract_month_bulletins(self, table_container, base_date: datetype) -> list[Bulletin]:
        bulletins = []
        
        month_str = table_container.find('h3').text
        month = month_to_number(month_str)
        monthly_date = base_date.replace(month=month)

        bulletin_divs = table_container.find_all('div', {'class': 'boib'})
        for bulletin_div in bulletin_divs:
            anchors = bulletin_div.find_all('a')
            for anchor in anchors:
                
                bulletins.append(
                    self.__extract_bulletin(anchor, monthly_date)
                )

        return bulletins
    
    def __extract_bulletin(self, anchor_element, base_date):
        bulletin_type = BulletinTypeFactory.from_anchor_class(anchor_element['class'])
        day = re.match(r'\d+', anchor_element.text).group(0)

        bulletin_date = base_date.replace(day=int(day))

        bulletin = Bulletin(
            type=bulletin_type, 
            date=bulletin_date, 
            url=f'{self.BASE_DOMAIN}{anchor_element['href']}', 
            sections=[]
        )

        bulletin.sections = self.__section_extractor.extract(bulletin)

        return bulletin


class CAIBSectionExtractor(CAIBBaseExtractor, SectionExtractor):

    def __init__(
        self, 
        article_extractor: ArticleExtractor = None,
    ):
        self.__article_extractor = article_extractor or CAIBArticleExtractor()
        self.__legacy_article_extractor = CAIBLegacyArticleExtractor()

    def extract(self, bulletin: Bulletin) -> list[Section]:
        soup = get_soup(bulletin.url)

        sections_list = soup.find('ul', {'class': 'primerosHijos'})
        if sections_list is not None:
           return self.__build_sections(sections_list)
        elif self.__is_legacy(soup):
            return self.__build_legacy_sections(bulletin, soup)
    
    def __build_sections(self, sections_list) -> list[Section]:
      
        section_items = sections_list.find_all('a', {'rel': 'section'})
        sections = []
        for section_item in section_items:
            section_em = section_item.find('em')

            section = Section(
                type=SectionTypeFactory.from_section_text(section_em.text),
                url=f'{self.BASE_DOMAIN}{section_item["href"]}',
                articles=[]
            )

            section.articles = self.__article_extractor.extract(section)

            sections.append(section)
        
        return sections
    
    def __build_legacy_sections(self, bulletin: Bulletin, soup) -> list[Section]:
        section = Section(
            type=SectionType.LEGACY,
            url=bulletin.url,
            articles=[]
        )

        section.articles = self.__legacy_article_extractor.extract_from_soup(soup)
         
        return [section]

    def __is_legacy(self, soup) -> bool:
        return soup.find('div', {'class': 'caja'})


class CAIBArticleExtractor(CAIBBaseExtractor, ArticleExtractor):

    def __init__(self):
        self.__grouped_article_extractor = CAIBGroupedArticleExtractor()
    
    def extract(self, section: Section) -> list[Article]:
        soup = get_soup(section.url)

        if self.__is_grouped(soup):
            return self.__grouped_article_extractor.extract_from_soup(soup)
        else: 
            return self.__build_articles(soup)
    
    def __build_articles(self, soup) -> list[Article]:
        articles_list = soup.find('ul', {'class': 'llistat'})
        article_items = articles_list.find_all('div', {'class': 'caja'})

        articles = []
        for article_item in article_items:
            organization = article_item.find('h3', {'class': 'organisme'}).text
            summary = article_item.find('ul', {'class': 'resolucions'}).find('p').text
            url_anchor = article_item.find('ul', {'class': 'documents'}).find('a', {'aria-label': 'Exportar a PDF'})
            url = url_anchor['href']
            if not url_is_absolute(url):
                url = f'{self.BASE_DOMAIN}{url}'

            article = Article(
                organization=organization,
                summary=summary,
                url=url,
            )

            articles.append(article)

        return articles

    def __is_grouped(self, soup) -> bool:
        return soup.find('div', {'class' : 'grupoPrincipal'}) is not None


class CAIBGroupedArticleExtractor(CAIBBaseExtractor, ArticleExtractor):
    
    def extract(self, section: Section) -> list[Article]:
        raise NotImplementedError('Grouped article extraction from section is not supported yet')

    def extract_from_soup(self, soup: BeautifulSoup) -> list[Article]:
        div_container = soup.find('div', {'class': 'grupoPrincipal'})

        organization_prefix = div_container.find('h2').text.split(' - ')[1]

        list_items = div_container.find('ul', {'class': 'llistat'}).find_all('li')

        last_organization = None

        articles = []
        for list_item in list_items:
            
            section_heading_item = list_item.find('h3')
            article_item = list_item.find('div', {'class': 'caja'})
            if section_heading_item is not None:
                last_organization = section_heading_item.text
            elif article_item is not None:
                summary = article_item.find('p').text
                url_anchor = article_item.find('a', {'class': 'pdf'})

                article = Article(
                    organization=f'{organization_prefix} {last_organization}',
                    summary=summary,
                    url=f'{self.BASE_DOMAIN}{url_anchor["href"]}',
                )

                articles.append(article)

        return articles


class CAIBLegacyArticleExtractor(CAIBBaseExtractor, ArticleExtractor):
    
    def extract(self, section: Section) -> list[Article]:
        raise NotImplementedError('Legacy article extraction from section is not supported yet')

    def extract_from_soup(self, soup: BeautifulSoup) -> list[Article]:
        articles_list = soup.find('ul', {'class': 'llistat'})
        article = articles_list.find('div', {'class': 'caja'})
        url_anchor = article.find('a', {'class': 'pdf'})

        article = Article(
            organization=None,
            summary=None,
            url=f'{self.BASE_DOMAIN}{url_anchor['href']}',
        )

        return [article]