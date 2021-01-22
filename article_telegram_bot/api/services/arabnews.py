from loguru import logger
from requests import Session

from ...tools import delete_duplicates
from ..utils import get_html_soup_by_url


class ArabNewsParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'https://www.arabnews.com'
        self.db_table_name = 'arabnews_table'
        self.database_rows_overflow_count = 300

    def get_latest_by_tag(self, tag: str):
        logger.debug(
            f'{self.__class__.__name__}: Get new articles list by tag {tag}...')

        uri = self.uri + '/' + tag
        soup = get_html_soup_by_url(self.requests_session, uri)
        article_list = soup.find_all('div', {'class': 'article-item'})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            article_info = item.find('div', {'class': 'article-item-info'})
            if article_info:
                item_link = article_info.find('a')
                if item_link:
                    updated_link = item_link.get('href')
                    items['article_list'].append(updated_link)

        return items

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        tags = [
            'lifestyle',
            'main-category/media',
            'sport',
            'economy',
            'world',
            'middleeast',
            'saudiarabia'
        ]

        latest_articles = []

        for tag in tags:
            tag_latest = self.get_latest_by_tag(tag)['article_list']
            latest_articles += tag_latest

        return delete_duplicates(latest_articles)

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)

        uri = self.uri + uri
        soup = get_html_soup_by_url(self.requests_session, uri)

        try:
            article_title = soup.find(
                'meta', {'property': 'og:title'}).get('content')
        except:
            article_title = None
        try:
            text_blocks = soup.find(
                'div', {'class': 'field-items'}).find_all('p')
        except:
            text_blocks = []

        try:
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
            article_text = '\n\n'.join(text_blocks_)
        except:
            article_text = None

        article_images = []

        article_body = {'title': article_title,
                        'source': uri,
                        'source_name': 'ArabNews',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
