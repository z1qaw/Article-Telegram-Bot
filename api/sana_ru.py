import re

from bs4 import BeautifulSoup
from urllib.parse import urlparse


class RuSanaParser:
    def __init__(self, requests_session):
        self.requests_session = requests_session
        self.uri = 'http://www.sana.sy/ru'
        self.db_table_name = 'ru_sana_table'

    def get_latest_by_tag(self, tag):

        get_uri = self.uri + tag

        answer = self.requests_session.get(get_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")
        article_block = soup.find('div', {'class': 'post-listing'})
        article_list = article_block.find_all('article', {'class': 'item-list'})

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            item_link = item.find('a', {'class': 'more-link'}).get('href')
            if item_link:
                updated_link = '/?' + urlparse(item_link).query
                items['article_list'].append(updated_link)

        return items

    def get_latest(self):
        print('BbcParser: Get new articles list...')

        tags = [
            '?cat=457',
            '?cat=447',
            '?cat=468',
            '?cat=477',
            '?cat=511',
            '?cat=581',
            '?cat=556',
            '?cat=495',
            '?cat=484',
            '?cat=545',
            '?cat=562',
            '?cat=538',
            '?cat=604'
        ]

        latest_articles = []

        for tag in tags:
            this_articles = self.get_latest_by_tag(tag)
            latest_articles += this_articles['article_list']

        return latest_articles

    def get_article(self, uri):
        print('BbcParser: Get article: ' + uri)

        article_uri = self.uri + uri
        answer = self.requests_session.get(article_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")

        try:
            article_title = soup.find('h1', {'class': re.compile('post-title')}).find('span', {'itemprop': 'name'}).text
        except:
            article_title = None

        new_text_blocks = []
        try:
            text_blocks = soup.find('div', {'class': re.compile('post-inner')}).find_all('p')
            related_block = soup.find('div', {'class': re.compile('post-inner')}).find('section',
                                                                                       {'id': 'related_posts'})
            for text_block in text_blocks:
                if related_block:
                    if re.findall(text_block.text.encode('unicode-escape').decode(), str(related_block)):
                        continue
                    else:
                        new_text_blocks.append(text_block)
                else:
                    new_text_blocks.append(text_block)
        except:
            pass

        try:
            article_main_image = soup.find('img', {'class': re.compile('attachment-slider')}).get('src')
        except:
            article_main_image = None

        article_pub_date = None

        text_blocks_ = []
        for block in new_text_blocks:
            text_blocks_.append(block.text)

        try:
            article_text = '\n\n'.join(text_blocks_)
        except:
            article_text = None

        article_images = []
        try:
            article_images_blocks = soup.find_all('figure', {'class': re.compile('gallery-item')})
            if article_images_blocks:
                for image_block in article_images_blocks:
                    image_uri = image_block.find('img')
                    if image_uri:
                        image_data_src = image_uri.get('src')
                        article_images.append(image_data_src)
        except:
            pass

        try:
            for block in new_text_blocks:
                image_block = block.find('img')
                if image_block:
                    article_images.append(image_block.get('src'))
        except:
            pass

        article_body = {'title': article_title,
                        'source': article_uri,
                        'source_name': 'Sana News RU',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'ru'}

        return article_body
