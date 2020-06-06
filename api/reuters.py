import tools

from bs4 import BeautifulSoup
from urllib.parse import urlparse


class ReutersParser:
    def __init__(self, requests_session):
        self.requests_session = requests_session
        self.uri = 'https://www.reuters.com'
        self.api_url = 'https://wireapi.reuters.com/v3/'
        self.db_table_name = 'reuters_table'

    def get_latest_by_tag(self, tag):
        if tag == 'world':
            tag = 'news/world'
        get_uri = self.api_url + 'feed/url/www.reuters.com/' + tag

        answer = self.requests_session.get(get_uri)
        answer_json = answer.json()
        article_list = answer_json['wireitems']

        items = {'tag': tag,
                 'article_list': []}

        for item in article_list:
            if item['templates'][0]['template'] == 'ad_basic':
                continue
            else:
                item_link = item['templates'][0]['story']['url']
                items['article_list'].append(urlparse(item_link).path)

        return items

    def get_latest(self):
        print('ReutersParser: Get new articles list...')

        tags = [
            'world',
            'politics'
        ]

        latest_articles = []
        for tag in tags:
            latest_articles += self.get_latest_by_tag(tag)['article_list']

        return latest_articles

    def get_article(self, uri):
        print('ReutersParser: Get article: ' + uri)

        article_uri = self.uri + uri
        answer = self.requests_session.get(article_uri)
        answer_html = answer.content.decode()
        soup = BeautifulSoup(answer_html, "html.parser")

        try:
            article_title = soup.find('h1', {'class': 'ArticleHeader_headline'}).text
        except:
            article_title = None

        text_blocks = soup.find('div', {'class': 'StandardArticleBody_body'}).find_all('p')

        article_main_image = None
        try:
            image_container = soup.find('div', {'class': 'PrimaryAsset_container'}).find('img')
            clean_src = image_container.get('src')
            article_main_image = 'https:' + tools.delete_query(clean_src, 'w')
        except:
            pass

        try:
            article_pub_date = soup.find('div', {'class': 'ArticleHeader_date'}).text
        except:
            article_pub_date = None

        text_blocks_ = []

        for block in text_blocks:
            if block.get('href'):
                continue
            else:
                text_blocks_.append(block.text)

        try:
            article_text = '\n\n'.join(text_blocks_)
        except:
            article_text = None

        article_images = []
        article_images_blocks = soup.find('div',
                                          {'class': 'StandardArticleBody_body'}).find_all('div',
                                                                                          {'class': 'Image_container'})
        if article_images_blocks:
            for image_block in article_images_blocks:
                image_uri_block = image_block.find('img')
                if image_uri_block:
                    image_data_src = image_uri_block.get('src')
                    article_images.append('https:' + tools.delete_query(image_data_src, 'w'))

        article_body = {'title': article_title,
                        'source': article_uri,
                        'source_name': 'Reuters.com',
                        'publish_date': article_pub_date,
                        'main_image_link': article_main_image,
                        'article_images': article_images,
                        'text': article_text,
                        'language': 'en'}

        return article_body
