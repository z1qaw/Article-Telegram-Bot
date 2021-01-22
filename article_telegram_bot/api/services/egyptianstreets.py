from urllib.parse import urlparse

from ..utils import get_html_soup_by_url
from loguru import logger
from requests import Session


class EgyptianStreetsParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'https://egyptianstreets.com'
        self.db_table_name = 'egyptianstreets_table'
        self.database_rows_overflow_count = 300

    def get_latest_by_tag(self, tag: str):
        logger.debug(
            f'{self.__class__.__name__}: Get new articles list by tag {tag}...')

        uri = self.uri + '/category/' + tag
        soup = get_html_soup_by_url(self.requests_session, uri)
        article_list = soup.find_all('li', {'class': 'infinite-post'})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find(
                'div', {'class': 'widget-full-list-text left relative'}).find('a')
            if item_link:
                items['article_list'].append(
                    urlparse(item_link.get('href')).path)

        return items

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')
        tags = [
            'politics-and-society/international-politics-and-society',
            'news-politics-and-society',
            'interviews',
            'opinion',
            'arts-culture',
            'technology-2',
            'tourism-2',
            'buzz'
        ]

        latest_articles = []

        for tag in tags:
            tag_articles = self.get_latest_by_tag(tag)
            latest_articles += tag_articles['article_list']

        return latest_articles

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)

        uri = self.uri + uri
        soup = get_html_soup_by_url(self.requests_session, uri)
        content = soup.find('div', {'id': 'content-area'})

        try:
            article_title = soup.find('meta', {'property': 'og:title'}).get(
                'content').replace(' | Egyptian Streets', '')
        except:
            article_title = None
        try:
            text_blocks = content.find_all('p')
        except:
            text_blocks = []

        try:
            article_main_image = None
            if soup.find('meta', {'name': 'twitter:image'}):
                article_main_image = soup.find(
                    'meta', {'name': 'twitter:image'}).get('content')
            if soup.find('meta', {'property': 'og:image'}):
                article_main_image = soup.find(
                    'meta', {'property': 'og:image'}).get('content')
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
            article_text = '\n\n'.join(text_blocks_).strip()
        except:
            article_text = None

        article_images = []
        article_images_blocks = content.find_all(
            'p') + content.find_all('figure')
        if article_images_blocks:
            for block in article_images_blocks:
                image_try = block.find('img')
                image_uri = None
                if image_try:
                    image_uri = image_try.get('src')
                if image_uri:
                    article_images.append(image_uri)

        article_body = {'title': article_title,
                        'source': uri,
                        'source_name': 'EgyptianStreets News',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
