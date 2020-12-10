import re
from urllib.parse import urlparse

from loguru import logger
from requests import Session

from ..utils import get_html_soup_by_url


class NnaParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'http://nna-leb.gov.lb/en'
        self.db_table_name = 'nna_table'

    def get_latest_by_tag(self, tag: str):
        logger.debug(
            f'{self.__class__.__name__}: Get new articles list by tag {tag}...')

        url = self.uri + '/news-categories/' + tag
        soup = get_html_soup_by_url(self.requests_session, url)

        article_list = soup.find(
            'div', {'class': 'pageview-list'}).find_all('div', {'class': 'bannerfeatured-item'})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find('h3').find('a').get('href')
            if item_link:
                updated_link = urlparse(item_link).path.replace('en/', '')
                items['article_list'].append(updated_link)

        return items

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        tags = [
            '1/Politics',
            '2/Security-Law',
            '4/Economy',
            '7/Sports',
            '6/Education-Culture',
            '3/Miscellaneous',
            '8/Regional',
            '9/International',
        ]

        latest_articles = []

        for tag in tags:
            this_articles = self.get_latest_by_tag(tag)
            latest_articles += this_articles['article_list']

        return latest_articles

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)

        url = self.uri + uri
        soup = get_html_soup_by_url(self.requests_session, url)

        try:
            article_title = soup.find(
                'meta', {'property': re.compile('og:title')}).get('content')
        except:
            article_title = None

        try:
            text_blocks = soup.find(
                'div', {'class': re.compile('article-content')}).find('p')
            if not text_blocks:
                text_blocks = soup.find(
                    'div', {'class': re.compile('article-content')})
        except:
            text_blocks = None

        try:
            article_main_image = soup.find(
                'meta', {'property': re.compile('og:image')}).get('content')
        except:
            article_main_image = None

        try:
            article_pub_date = soup.find(
                'meta', {'itemprop': 'datePublished'}).get('content')
        except:
            article_pub_date = None

        try:
            article_text = text_blocks.text
        except:
            article_text = None

        article_images = []

        article_body = {'title': article_title,
                        'source': url,
                        'source_name': 'NNA News',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
