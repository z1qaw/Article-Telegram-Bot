from urllib.parse import urlparse

from requests.sessions import session

from loguru import logger
from requests import Session

from ... import tools
from ..utils import get_html_soup_by_url, parse_iso_8601_time


class ReutersParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'https://www.reuters.com/'
        self.db_table_name = 'reuters_table'

    def get_latest_by_tag(self, tag: str):
        logger.debug(
            f'{self.__class__.__name__}: Get new articles list by tag {tag}...')

        if tag == 'world':
            tag = 'news/world'

        url = self.uri + tag

        soup = get_html_soup_by_url(self.requests_session, url)
        article_list = soup.find_all(
            'article', {'class': 'story'}
        )

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            article_url = item.find('a').get('href')
            items['article_list'].append(article_url)

        return items

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        tags = [
            'world',
            'politics'
        ]

        latest_articles = []
        for tag in tags:
            latest_articles += self.get_latest_by_tag(tag)['article_list']

        return latest_articles

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)

        url = self.uri + uri
        print(url)
        soup = get_html_soup_by_url(self.requests_session, url)

        try:
            article_title = soup.find(
                'meta', {'property': 'og:title'}).get('content')
        except:
            article_title = None

        text_blocks = soup.find(
            'div', {'class': 'ArticleBodyWrapper'}).find_all('p')

        try:
            article_main_image = soup.find(
                'meta', {'property': 'og:image'}).get('content')
        except:
            article_main_image = None

        try:
            article_pub_date = parse_iso_8601_time(soup.find(
                'meta', {'property': 'og:article:published_time'}).get('content'))
        except:
            article_pub_date = None

        text_blocks_ = []

        for block in text_blocks:
            if block.get('href'):
                continue
            else:
                text_blocks_.append(block.text)

        try:
            article_text = '\n\n'.join(text_blocks_)
        except:
            article_text = None

        article_images = []

        article_body = {'title': article_title,
                        'source': url,
                        'source_name': 'Reuters.com',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
