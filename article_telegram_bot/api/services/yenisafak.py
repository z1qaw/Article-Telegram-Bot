import re

import requests
from bs4 import BeautifulSoup
from loguru import logger


class YeniSafakParser:
    def __init__(self, requests_session: requests.Session):
        self.requests_session = requests_session
        self.uri = 'https://www.yenisafak.com'
        self.db_table_name = 'yenisafak_table'

    def get_latest_by_tag(self, tag: str):
        get_uri = self.uri + '/en/' + tag

        answer = self.requests_session.get(get_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")
        article_list = soup.find('div', {'class': 'list-news'}).find_all('article')

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find('a')
            if item_link:
                updated_link = item_link.get('href')
                items['article_list'].append(updated_link)

        return items

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        tags = [
            'turkeyeconomy',
            'current',
            'local-news',
            'arts-culture'
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
            article_title = soup.find('h1', {'class': 'title'}).text
        except:
            article_title = None
        try:
            text_blocks = soup.find('article', {'class': re.compile('main')}).find_all('p')
        except:
            text_blocks = []

        try:
            article_main_image = soup.find('meta', {'property': 'og:image'}).get('content')
        except:
            article_main_image = None

        try:
            article_pub_date = soup.find('div', {'class': re.compile('info')}).find('time').text
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

        article_body = {'title': article_title,
                        'source': article_uri,
                        'source_name': 'YeniSafak News',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
