import re

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class IranTodayParser:
    def __init__(self, requests_session):
        self.requests_session = requests_session
        self.uri = 'http://iransegodnya.ru'
        self.db_table_name = 'irant_table'

    def get_latest(self):
        print('IranToday: Get new articles list...')
        get_uri = self.uri + '/news'

        answer = self.requests_session.get(get_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")
        article_list = soup.find_all('article', {'class': 'news-line'})

        latest_articles = []

        for article in article_list:
            article_uri = urlparse(article.find('a').get('href')).path
            latest_articles.append(article_uri)

        return latest_articles

    def get_article(self, uri):
        print('IranToday: Get article: ' + uri)

        article_uri = self.uri + uri
        answer = self.requests_session.get(article_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")

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
                        'source': article_uri,
                        'source_name': 'IranToday',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'ru'}

        return article_body
