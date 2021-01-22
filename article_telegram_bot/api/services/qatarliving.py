from urllib.parse import urlparse

from loguru import logger
from requests import Session

from ..utils import get_html_soup_by_url, parse_iso_8601_time


class QatarLivingParser:
    def __init__(self, requests_session: Session):
        self.requests_session = requests_session
        self.uri = 'https://www.qatarliving.com'
        self.db_table_name = 'qatarliving_table'
        self.database_rows_overflow_count = 300

    def get_latest_by_tag(self, tag: str):
        logger.debug(
            f'{self.__class__.__name__}: Get new articles list by tag {tag}...')

        get_uri = self.uri + tag

        soup = get_html_soup_by_url(self.requests_session, get_uri)
        article_list = soup.find(
            'div', {'class': 'b-topic-post'}).find_all('div', {'id': 'post-page'})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find('a', {'class': 'b-topic-post--el-title'})
            if item_link:
                updated_link = urlparse(item_link.get('href')).path
                items['article_list'].append(updated_link)

        return items

    def get_latest(self):
        logger.info(f'{self.__class__.__name__}: Get new articles list...')

        tags = [
            '/forum/news/'
        ]

        latest_articles = []

        for tag in tags:
            latest_articles += self.get_latest_by_tag(tag)['article_list']

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
                'div', {'class': 'b-post-detail--el-text'}).find_all('p')
        except:
            text_blocks = []

        try:
            article_main_image = soup.find(
                'meta', {'property': 'og:image'}).get('content')
        except:
            article_main_image = None

        try:
            article_pub_date = parse_iso_8601_time(soup.find(
                'meta', {'name': 'dcterms.date'}).get('content'))
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
        article_images_blocks = text_blocks
        if article_images_blocks:
            for block in article_images_blocks:
                image_uri = block.find('img')
                if image_uri:
                    image_data_src = image_uri.get('src')
                    article_images.append(image_data_src)

        article_body = {'title': article_title,
                        'source': article_uri,
                        'source_name': 'QatarLiving News',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
