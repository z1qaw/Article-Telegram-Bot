import re

from loguru import logger
from requests import Session

from ..utils import get_html_soup_by_url


class InoSmiParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'https://inosmi.ru'
        self.db_table_name = 'inosmi_table'

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        url = self.uri + '/today'
        soup = get_html_soup_by_url(self.requests_session, url)

        article_block = soup.find(
            'section', {'class': re.compile('rubric-list')})
        articles_blocks = article_block.find_all(
            'article', {'class': 'rubric-list__article'})

        items = []

        for item in articles_blocks:
            item_link = item.find('a', {'class': 'rubric-list__article-image'})
            if item_link:
                items.append(item_link.get('href'))

        return items

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)

        url = self.uri + uri
        soup = get_html_soup_by_url(self.requests_session, url)

        try:
            article_title = soup.find(
                'h1', {'class': re.compile('article-header__title')}).text
        except:
            article_title = None

        try:
            text_blocks = soup.find(
                'div', {'class': re.compile('article-body')}).find_all('p')
        except:
            text_blocks = []

        try:
            article_main_image = soup.find(
                'span', {'class': re.compile('fs-article-trigger')}).find('img').get('src')
        except:
            article_main_image = None

        try:
            article_pub_date = soup.find(
                'meta', {'property': 'article:published_time'}).get('content')
        except:
            article_pub_date = None

        text_blocks_ = []

        for block in text_blocks:
            text_blocks_.append(block.text)

        try:
            article_text = '\n\n'.join(text_blocks_)
        except:
            article_text = None

        article_images = []
        article_images_blocks = soup.find_all(
            'img', {'class': re.compile('widgetImage__image')})
        if article_images_blocks:
            for image_block in article_images_blocks:
                image_uri = image_block.get('data-src')
                if image_uri:
                    article_images.append('https:' + image_uri)

        article_body = {'title': article_title,
                        'source': url,
                        'source_name': 'InoSmi',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'ru'}

        return article_body
