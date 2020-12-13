import re
import time
from urllib.parse import urlsplit

from loguru import logger
from requests import Session

from ..utils import get_html_soup_by_url


class BbcParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'https://www.bbc.com'
        self.db_table_name = 'bbc_table'

    def get_latest_by_tag(self, tag: str):
        logger.debug(
            f'{self.__class__.__name__}: Get new articles list by tag {tag}...')

        url = self.uri + '/news/' + tag
        soup = get_html_soup_by_url(self.requests_session, url)
        article_list = soup.find_all('article', {'class': 'lx-stream-post'})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find('a', {'class': 'qa-heading-link'})
            if item_link:
                updated_link = urlsplit(item_link.get(
                    'href'))._replace(query=None).geturl()
                items['article_list'].append(updated_link)

        return items

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        tags = [
            'world',
            'business',
            'science_and_environment'
        ]

        latest_articles = []

        for tag in tags:
            latest_articles += self.get_latest_by_tag(tag)['article_list']

        return latest_articles

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)

        url = self.uri + uri
        soup = get_html_soup_by_url(self.requests_session, url)

        try:
            article_title = soup.find(
                'meta', {'property': 'og:title'}).get('content')
        except:
            article_title = None
        try:
            text_blocks = soup.find_all(
                'div', {'class': re.compile('RichTextComponentWrapper')})
        except:
            text_blocks = []

        try:
            article_main_image = soup.find(
                'meta', {'property': 'og:image'}).get('content')
        except:
            article_main_image = None

        try:
            article_pub_date = time.ctime(
                int(soup.find('div', {'class': 'date date--v2'}).get('data-seconds')))
        except:
            article_pub_date = None

        text_blocks_ = []

        for block in text_blocks:
            if block.find('p'):
                text = block.find('p').text
                text = re.sub(
                    '\.css\-\w+\-\w+Text\{font\-\w+\:\w+\;\}', '', text)
                if re.search('\.css', text):
                    continue
                text_blocks_.append(text)

        try:
            article_text = '\n\n'.join(text_blocks_)
        except:
            article_text = None

        article_images = []

        article_body = {'title': article_title,
                        'source': url,
                        'source_name': 'BBC News',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
