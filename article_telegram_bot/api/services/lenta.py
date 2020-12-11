import re
import time
from urllib.parse import urlparse

from requests import Session
from loguru import logger

from ..utils import get_html_soup_by_url


class LentaParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'https://lenta.ru'
        self.db_table_name = 'lenta_table'

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        url = self.uri + '/parts/news/'
        soup = get_html_soup_by_url(self.requests_session, url)
        article_blocks = soup.find_all(
            'div', {
                'class': re.compile('(item.+news)|(news.+item)')
            }
        )

        latest_articles = list(map(
            lambda article_block: article_block
            .find('h3')
            .find('a')
            .get('href'),
            article_blocks
        ))

        latest_articles = list(filter(
            lambda article_uri: False if re.search(
                'moslenta', article_uri) else True,
            latest_articles
        ))

        return latest_articles

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)
        url = self.uri + uri

        try:
            soup = get_html_soup_by_url(self.requests_session, url)

            try:
                article_title = soup.find('h1').text
            except:
                article_title = None

            try:
                article_main_image = soup \
                    .find(
                        'div', {'class': re.compile('b-topic__title-image')}) \
                    .find('img') \
                    .get('src')
            except:
                article_main_image = None

            try:
                article_pub_date = soup \
                    .find('time', {'class': re.compile('g-date')}) \
                    .text
            except:
                article_pub_date = None

            article_uri = url

            try:
                pure_text_blocks = []
                html_text_blocks = soup.find(
                    'div', {'class': re.compile('b-text')}).find_all(
                        'p'
                )
                for block in html_text_blocks:
                    text = block.text
                    cleaned_text = re.sub('<[^>]+>', '', text)
                    pure_text_blocks.append(cleaned_text)
                pure_text = '\n\n'.join(pure_text_blocks)
            except:
                pure_text = ''

            article_images = []
            article_body = {'title': article_title,
                            'source': article_uri,
                            'source_name': 'Lenta.Ru',
                            'publish_date': article_pub_date,
                            'main_image_link': article_main_image,
                            'article_images': article_images,
                            'text': pure_text,
                            'language': 'ru'}

            return article_body
        except:
            return None
