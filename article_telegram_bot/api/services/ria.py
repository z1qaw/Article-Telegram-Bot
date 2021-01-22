import re

import requests
from bs4 import BeautifulSoup
from loguru import logger


class RiaParser:
    def __init__(self, requests_session: requests.Session):
        self.requests_session = requests_session
        self.uri = 'https://ria.ru'
        self.db_table_name = 'ria_table'
        self.database_rows_overflow_count = 300

    def get_latest_by_tag(self, tag: str):
        logger.debug(
            f'{self.__class__.__name__}: Get new articles list by tag {tag}...')
        get_uri = self.uri + '/services/tagsearch'
        get_params = {'date_start': None,
                      'date': None,
                      'tags[]': [tag]}

        answer = self.requests_session.get(get_uri, params=get_params)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")
        article_list = soup.find_all('div', {'class': 'list-item'})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find(
                'a', {'class': re.compile('list-item__title*')}).get('href')
            items['article_list'].append(item_link)

        return items

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')
        tags = [
            'politics',
            'society',
            'economy',
            'world',
            'incidents',
            'religion'
        ]

        latest_articles = []

        for tag in tags:
            latest_articles += self.get_latest_by_tag(tag)['article_list']

        return latest_articles

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)

        article_uri = self.uri + uri
        answer = self.requests_session.get(article_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")

        try:
            article_title = soup.find('h1', {'article__title'}).text
        except:
            article_title = None

        text_blocks = soup.find_all(
            'div', {'class': 'article__block', 'data-type': 'text'})
        try:
            article_main_image = soup.find('div', {'class': 'article__announce'}).find('div', {
                'class': 'photoview__open'}).get('data-photoview-src')
        except:
            article_main_image = None

        try:
            article_pub_date = soup.find(
                'div', {'class': 'article__info-date'}).find('a').text
        except:
            article_pub_date = None

        text_blocks_ = []

        for block in text_blocks:
            text_blocks_.append(block.find(
                'div', {'class': re.compile('article__text')}).text)

        try:
            article_text = '\n\n'.join(text_blocks_)
        except:
            article_text = None

        article_images = []
        article_images_blocks = soup.find_all(
            'div', {'class': 'article__block', 'data-type': 'media'})
        if article_images_blocks:
            for image_block in article_images_blocks:
                image_uri = image_block.find(
                    'div', {'class': 'photoview__open'})
                if image_uri:
                    image_data_src = image_uri.get('data-photoview-src')
                    article_images.append(image_data_src)

        article_body = {'title': article_title,
                        'source': article_uri,
                        'source_name': 'РИА Новости',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'ru'}

        return article_body
