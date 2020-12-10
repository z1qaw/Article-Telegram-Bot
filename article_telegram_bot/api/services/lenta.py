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
        article_block_list = soup.find_all('div', {'class': 'item news'})

        latest_articles = list(map(
            lambda article_block: article_block.find('a').get('href'),
            article_block_list
        ))

        return latest_articles

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)
        url = self.uri + uri

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
                .find('time', {'class': 'g-date'}) \
                .text
        except:
            article_pub_date = None


        try:
            response = self.requests_session.get(url)
            response = response.json()

            blocks = response['topic']['body']

            article_title = response['topic']['headline']['info']['title']
            article_uri = response['topic']['headline']['links']['public']
            article_pub_date = time.ctime(
                response['topic']['headline']['info']['modified'])

            text_blocks = []
            for block in blocks:
                if block['type'] == 'p':
                    cleaned_text = re.sub('<[^>]+>', '', block['content'])
                    text_blocks.append(cleaned_text)

            pure_text = '\n\n'.join(text_blocks)

            article_images = []
            article_main_image = response['topic']['headline']['title_image']['url']

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
