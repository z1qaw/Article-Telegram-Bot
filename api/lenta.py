import re
import time

from urllib.parse import urlparse


class LentaParser:
    def __init__(self, requests_session):
        self.requests_session = requests_session
        self.uri = 'https://api.lenta.ru'
        self.db_table_name = 'lenta_table'

    def get_latest(self):
        """:return list of articles links"""
        print('LentaParser: Get new articles list...')
        response = self.requests_session.get(self.uri + '/lists/latest')
        full_list = response.json()['headlines']

        uri_list = []
        for article_preview in full_list:
            uri_list.append(urlparse(article_preview['links']['self']).path)

        return uri_list

    def get_article(self, uri):
        print('LentaParser: Get article: ' + uri)
        complete_url = self.uri + uri

        try:
            response = self.requests_session.get(complete_url)
            response = response.json()

            blocks = response['topic']['body']

            article_title = response['topic']['headline']['info']['title']
            article_uri = response['topic']['headline']['links']['public']
            article_pub_date = time.ctime(response['topic']['headline']['info']['modified'])

            text_blocks = []
            for block in blocks:
                if block['type'] == 'p':
                    cleaned_text = re.sub('<[^>]+>', '', block['content'])
                    text_blocks.append(cleaned_text)

            pure_text = '\n\n'.join(text_blocks)

            article_images = []
            article_main_image = response['topic']['headline']['title_image']['url']

            article_body = {'title': article_title,
                            'source': article_uri,
                            'source_name': 'Lenta.Ru',
                            'publish_date': article_pub_date,
                            'main_image_link': article_main_image,
                            'article_images': article_images,
                            'text': pure_text,
                            'language': 'ru'}

            return article_body

        except:
            return None
