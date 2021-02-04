import datetime
import re

import requests
import urllib3
from bs4 import BeautifulSoup
from loguru import logger

from ..utils import get_html_soup_by_url, parse_iso_8601_time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TourpromParser:
    def __init__(self, requests_session: requests.Session):
        self.requests_session = requests_session
        self.uri = 'https://www.tourprom.ru'
        self.db_table_name = 'tourprom_table'
        self.database_rows_overflow_count = 300

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')
        tags = [
            '/news',
            '/pressreleases'
        ]

        articles_uri = []
        for tag in tags:
            get_uri = self.uri + tag
            answer = self.requests_session.get(get_uri, verify=False)
            answer_html = answer.content.decode()
            soup = BeautifulSoup(answer_html, "html.parser")

            articles_block = soup.find(
                'div', {'class': 'block news-list__list'})

            articles_blocks = None
            if tag == '/news':
                articles_blocks = articles_block.find_all(
                    'div', {'class': 'news-list__item-wrap'})
            elif tag == '/pressreleases':
                articles_blocks = articles_block.find_all(
                    'div', {'class': 'pressrelease-item'})

            for block in articles_blocks:
                title_uri = None
                if tag == '/news':
                    header_block = block.find('h3')
                    header_text_block = header_block.find('a')
                    title_uri = header_text_block.get('href')
                elif tag == '/pressreleases':
                    header_block = block.find('h2')
                    header_text_block = header_block.find('a')
                    title_uri = header_text_block.get('href')
                if title_uri:
                    articles_uri.append(title_uri)

        return articles_uri

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)

        try:
            article_uri = self.uri + uri
            soup = get_html_soup_by_url(
                self.requests_session, article_uri, verify=False)
            article_block = soup.find('div', {'class': 'panel'})

            try:
                article_title = article_block.find('h1').text
            except:
                article_title = None

            text_block = None
            if 'pressrelease' in uri:
                text_block = article_block.find(
                    'div', {'class': re.compile('block block--padding')})
            elif 'news' in uri:
                text_block = article_block.find(
                    'div', {'class': re.compile('block panel-body-wrap--padding news-detail')})

            text_blocks = text_block.find_all('p')

            try:
                article_main_image = self.uri + article_block.find('div', {'class': 'photo-wrap'}).find('img', {
                    'class': 'photo__img'}).get('src')
            except:
                article_main_image = None

            text_blocks_ = []

            for block in text_blocks:
                if not re.search('Подпишитесь на новости', block.text):
                    text_blocks_.append(block.text)

            try:
                article_text = '\n\n'.join(text_blocks_)
            except:
                article_text = None

            article_body = {'title': article_title,
                            'source': article_uri,
                            'source_name': 'TourProm.ru',
                            'publish_date': str(datetime.datetime.now()),
                            'main_image_link': article_main_image,
                            'article_images': [],
                            'text': article_text,
                            'language': 'ru'}
            return article_body
        except:
            return None
