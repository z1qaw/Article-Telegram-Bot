import re

from loguru import logger
from requests import Session

from ...tools import delete_duplicates
from ..utils import get_html_soup_by_url, parse_iso_8601_time


class EgyptTodayParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'https://www.egypttoday.com'
        self.db_table_name = 'egypttoday_table'
        self.database_rows_overflow_count = 300

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        uri = self.uri + '/Section/LoadMoreSectionArt?secID=1&pageNum=1&pageSize=30'

        soup = get_html_soup_by_url(self.requests_session, uri)
        article_list = soup.find_all(
            'div', {'class': re.compile('Sectionnewsitem')})

        latest_articles = []

        for item in article_list:
            item_link = item.find('a')
            if item_link:
                updated_link = item_link.get('href')
                latest_articles.append(updated_link)

        return delete_duplicates(latest_articles)

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
            text_block = soup.find('div', {'id': 'newsbody'})
            if text_block:
                text_block = text_block.find(
                    'p').text.strip().replace('\t', '')
            else:
                pure_article_blocks = []
                text_blocks = soup.find(
                    'div', {'class': 'ArticleDescription'}).find_all('div')
                if not text_blocks:
                    text_blocks = soup.find(
                        'div', {'class': 'ArticleDescription'}).find_all('p')
                for block in text_blocks:
                    block_text = block.text.strip()
                    if not block_text:
                        continue
                    else:
                        pure_article_blocks.append(block_text)
                text_block = '\n\n'.join(pure_article_blocks).replace('\t', '')

        except:
            text_block = ''

        try:
            article_main_image = soup.find(
                'meta', {'property': 'og:image'}).get('content')
        except:
            article_main_image = None

        try:
            article_pub_date = parse_iso_8601_time(soup.find(
                'meta', {'property': 'article:published_time'}
            ).get('content'))
        except:
            article_pub_date = None

        article_body = {'title': article_title,
                        'source': article_uri,
                        'source_name': 'EgyptToday News',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': [],
                        'text': text_block,
                        'language': 'en'}

        return article_body
