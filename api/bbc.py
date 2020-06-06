import time

from bs4 import BeautifulSoup
from urllib.parse import urlsplit


class BbcParser:
    def __init__(self, requests_session):
        self.requests_session = requests_session
        self.uri = 'https://www.bbc.com'
        self.db_table_name = 'bbc_table'

    def get_latest_by_tag(self, tag):

        get_uri = self.uri + '/news/' + tag

        answer = self.requests_session.get(get_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")
        article_list = soup.find_all('article', {'class': 'lx-stream-post'})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find('a', {'class': 'qa-heading-link'})
            if item_link:
                updated_link = urlsplit(item_link.get('href'))._replace(query=None).geturl()
                items['article_list'].append(updated_link)

        return items

    def get_latest(self):
        print('BbcParser: Get new articles list...')

        tags = [
            'world',
            'business',
            'science_and_environment'
        ]

        latest_articles = []

        for tag in tags:
            latest_articles += self.get_latest_by_tag(tag)['article_list']

        return latest_articles

    def get_article(self, uri):
        print('BbcParser: Get article: ' + uri)

        article_uri = self.uri + uri
        answer = self.requests_session.get(article_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")

        try:
            article_title = soup.find('h1', {'class': 'story-body__h1'}).text
        except:
            article_title = None
        try:
            text_blocks = soup.find('div', {'class': 'story-body__inner'}).find_all('p')
        except:
            text_blocks = []

        try:
            article_main_image = soup.find('img', {'class': 'js-image-replace'}).get('src')
        except:
            article_main_image = None

        try:
            article_pub_date = time.ctime(int(soup.find('div', {'class': 'date date--v2'}).get('data-seconds')))
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
        article_images_blocks = soup.find_all('figure', {'class': 'media-landscape'})
        if article_images_blocks:
            for image_block in article_images_blocks:
                image_uri = image_block.find('img', {'class': 'responsive-image__img'})
                if image_uri:
                    image_data_src = image_uri.get('src')
                    article_images.append(image_data_src)

        article_body = {'title': article_title,
                        'source': article_uri,
                        'source_name': 'BBC News',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
