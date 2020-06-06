import re

from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlparse


class YOmanParser:
    def __init__(self, requests_session):
        self.requests_session = requests_session
        self.uri = 'https://www.y-oman.com'
        self.db_table_name = 'y_oman_table'

    def get_latest_by_tag(self, tag):

        get_uri = self.uri + tag

        answer = self.requests_session.get(get_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")

        article_list = soup.find_all('div', {'class': re.compile('cell-style-1')})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find('a', {'class': 'clearfix'})
            if item_link:
                updated_link = urlparse(urlsplit(item_link.get('href'))._replace(query=None).geturl()).path
                items['article_list'].append(updated_link)

        return items

    def get_latest(self):
        print('YOmanParser: Get new articles list...')

        tags = [
            '/category/money/',
            '/category/business/',
            '/category/tech/',
            '/category/sport/',
            '/category/culture/',
            '/category/lifestyle/',
            '/category/in-town/events/'
        ]

        latest_articles = []

        for tag in tags:
            latest_articles += self.get_latest_by_tag(tag)['article_list']

        return latest_articles

    def get_article(self, uri):
        print('YOmanParser: Get article: ' + uri)

        article_uri = self.uri + uri
        answer = self.requests_session.get(article_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")

        try:
            article_title = soup.find('h1').text
        except:
            article_title = None

        try:
            text_blocks = soup.find('div', {'class': re.compile('detail-page-left')}).find_all('p')
        except:
            text_blocks = []

        try:
            article_main_image = soup.find('meta', {'property': 'og:image'}).get('content')
        except:
            article_main_image = None

        try:
            article_pub_date = soup.find('meta', {'property': 'article:published_time'}).get('content')
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
        article_images_blocks = soup.find('div', {'class': re.compile('detail-page-left')}).find_all('img', {'class': re.compile('alignnone')})
        if article_images_blocks:
            for image_block in article_images_blocks:
                if image_block:
                    image_data_src = image_block.get('src')
                    article_images.append(image_data_src)

        article_body = {'title': article_title,
                        'source': article_uri,
                        'source_name': 'Y-Oman News',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
