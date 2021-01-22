import re

from loguru import logger
from requests import Session

from ..utils import get_html_soup_by_url


class ArabianBusinessParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'https://www.arabianbusiness.com'
        self.db_table_name = 'arabianbusiness_table'
        self.database_rows_overflow_count = 300
        self.request_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers',
            'Sec-GPC': '1'
        }

    def get_latest_by_tag(self, tag: str):
        logger.debug(
            f'{self.__class__.__name__}: Get new articles list by tag {tag}...')

        url = self.uri + '/' + tag
        soup = get_html_soup_by_url(
            self.requests_session, url, self.request_headers)

        article_block = soup.find(
            'div', {'class': re.compile('custom-trending-tag')})
        article_list = article_block.find_all(
            'div', {'class': re.compile('trd-tags')})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find('h3', {'class': re.compile(
                'main-lead-text')}).find('a').get('href')
            if item_link:
                items['article_list'].append(item_link)

        return items

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        tags = [
            'industries',
            'galleries',
            'gcc',
            'interviews',
            'lifestyle',
            'property'
        ]

        latest_articles = []

        for tag in tags:
            latest_articles += self.get_latest_by_tag(tag)['article_list']

        return latest_articles

    def get_article(self, uri: str):
        logger.info(f'{self.__class__.__name__}: Get article: ' + uri)

        url = self.uri + uri
        soup = get_html_soup_by_url(
            self.requests_session, url, self.request_headers)

        try:
            article_title = soup.find(
                'h1', {'class': re.compile('news-title|main-bg-title')}).text
        except:
            article_title = None
        try:
            text_blocks = soup.find(
                'div', {'class': 'news-data'}).find_all('p')
        except:
            text_blocks = []

        try:
            article_main_image = soup.find(
                'meta', {'property': re.compile('og:image')}).get('content')
        except:
            article_main_image = None

        try:
            article_pub_date = soup.find('div', {'class': re.compile(
                'date-published')}).find('span', {'class': re.compile('d-t')}).text
        except:
            article_pub_date = None

        text_blocks_ = []

        for block in text_blocks:
            text_blocks_.append(block.text)

        try:
            article_text = '\n\n'.join(text_blocks_)
            while re.findall('\n\n\n|\r|\t', article_text):
                article_text = article_text.replace('\t', '').replace(
                    '\n\n\n', '\n\n').replace('\r', '')
        except:
            article_text = None

        article_images = []
        article_images_blocks = soup.find_all(
            'img', {'class': re.compile('media-element')})

        if article_images_blocks:
            for image_block in article_images_blocks:
                image_uri = image_block.get('src')
                if image_uri:
                    article_images.append(image_uri)

        article_body = {'title': article_title,
                        'source': url,
                        'source_name': 'Arabian Business News',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
