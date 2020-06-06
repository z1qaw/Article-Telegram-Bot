import re

from bs4 import BeautifulSoup
from urllib.parse import urlparse


class NnaParser:
    def __init__(self, requests_session):
        self.requests_session = requests_session
        self.uri = 'http://nna-leb.gov.lb/en'
        self.db_table_name = 'nna_table'

    def get_latest_by_tag(self, tag):

        get_uri = self.uri + '/news-categories/' + tag

        answer = self.requests_session.get(get_uri)
        answer_html = answer.text
        soup = BeautifulSoup(answer_html, "html.parser")
        article_list = soup.find('div', {'class': 'pageview-list'}).find_all('div', {'class': 'bannerfeatured-item'})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find('h3').find('a').get('href')
            if item_link:
                updated_link = urlparse(item_link).path.replace('en/', '')
                items['article_list'].append(updated_link)

        return items

    def get_latest(self):
        print('NnaParser: Get new articles list...')

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

    def get_article(self, uri):
        print('NnaParser: Get article: ' + uri)

        article_uri = self.uri + uri
        answer = self.requests_session.get(article_uri)
        answer_html = answer.text
        soup = BeautifulSoup(answer_html, "html.parser")

        try:
            article_title = soup.find('meta', {'property': re.compile('og:title')}).get('content')
        except:
            article_title = None

        try:
            text_blocks = soup.find('div', {'class': re.compile('article-content')}).find('p')
            if not text_blocks:
                text_blocks = soup.find('div', {'class': re.compile('article-content')})
        except:
            text_blocks = None

        try:
            article_main_image = soup.find('meta', {'property': re.compile('og:image')}).get('content')
        except:
            article_main_image = None

        try:
            article_pub_date = soup.find('meta', {'itemprop': 'datePublished'}).get('content')
        except:
            article_pub_date = None

        try:
            article_text = text_blocks.text
        except:
            article_text = None

        article_images = []

        article_body = {'title': article_title,
                        'source': article_uri,
                        'source_name': 'NNA News',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
