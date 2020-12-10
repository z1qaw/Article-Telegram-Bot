import re
from urllib.parse import urlparse

from requests import Session
from loguru import logger
from ..utils import get_html_soup_by_url


class IranTodayParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'http://iransegodnya.ru'
        self.db_table_name = 'irant_table'

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        url = self.uri + '/news'
        soup = get_html_soup_by_url(self.requests_session, url)
        article_list = soup.find_all('article', {'class': 'news-line'})

        latest_articles = list(map(
            lambda article_block: urlparse(
                article_block.find('a').get('href')).path,
            article_list
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

        article_main_image = None

        try:
            article_pub_date = soup.find('div', {'class': 'date'}).text
        except:
            article_pub_date = None

        text_block = soup.find('div', {'class': re.compile('post-content')})
        text_blocks = text_block.find_all('p')
        text_blocks_ = []
        article_images = []

        for block in text_blocks:
            if block.text:
                if not re.findall('^\n\d+$', block.text):
                    text_blocks_.append(block.text)
            block_images = block.find_all('img')
            if block_images:
                for img in block_images:
                    article_images.append(img.get('src'))

        try:
            article_text = '\n\n'.join(text_blocks_)
        except:
            article_text = None

        article_body = {'title': article_title,
                        'source': url,
                        'source_name': 'IranToday',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'ru'}

        return article_body
