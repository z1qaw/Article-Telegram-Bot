import re

from loguru import logger
from requests import Session

from ..utils import get_html_soup_by_url


class MehrNewsParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'https://en.mehrnews.com'
        self.db_table_name = 'mehrnews_table'
        self.database_rows_overflow_count = 300

    def get_latest_by_tag(self, tag: str):
        logger.debug(
            f'{self.__class__.__name__}: Get new articles list by tag {tag}...')

        get_uri = self.uri + '/service/' + tag
        soup = get_html_soup_by_url(self.requests_session, get_uri)
        article_list = soup.find_all(
            'li', {'class': re.compile('news|report')})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find('h3').find('a')
            if item_link:
                updated_link = item_link.get('href')
                items['article_list'].append(updated_link)

        return items

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        tags = [
            'iran',
            'World',
            'politics',
            'economy',
            'culture',
            'technology',
            'sports',
            'opinion'
        ]

        latest_articles = []

        for tag in tags:
            tag_latest = self.get_latest_by_tag(tag)['article_list']
            latest_articles += tag_latest

        return latest_articles

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)

        article_uri = self.uri + uri
        soup = get_html_soup_by_url(self.requests_session, article_uri)

        try:
            article_title = soup.find(
                'meta', {'property': 'og:title'}).get('content')
        except:
            article_title = None

        try:
            text_blocks = soup.find(
                'div', {'class': 'item-body'}).find_all('p')
        except:
            text_blocks = []

        try:
            article_main_image = soup.find(
                'meta', {'property': 'og:image'}).get('content')
        except:
            article_main_image = None

        try:
            article_pub_date = soup.find(
                'meta', {'property': 'article:modified'}).get('content')
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
        article_images_blocks = soup.find_all('figure')
        if article_images_blocks:
            for image_block in article_images_blocks:
                image_uri = image_block.find('img')
                if image_uri:
                    image_data_src = image_uri.get('src')
                    article_images.append(image_data_src)

        article_body = {'title': article_title,
                        'source': article_uri,
                        'source_name': 'MehrNews',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images[1:],
                        'text': article_text,
                        'language': 'en'}
        return article_body
