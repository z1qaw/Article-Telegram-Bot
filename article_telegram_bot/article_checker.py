from loguru import logger
import json
import colorama
import secrets
import string

from . import tools

colorama.init()


class Article:
    def __init__(self, article_body):
        self.id = ''.join(secrets.choice(
            string.ascii_letters + string.digits) for i in range(8))
        self.article_body = article_body
        self.title = article_body['title']
        self.source = article_body['source']
        self.source_name = article_body['source_name']
        self.publish_date = article_body['publish_date']
        self.main_image_link = article_body['main_image_link']
        self.article_images = article_body['article_images']
        self.text = article_body['text']
        self.match_words = []
        self.new = 0
        self.match = 0
        self.language = article_body['language']
        self.send_key_words = True

    def __str__(self):
        match_text = '\nMatch:' + \
            ', '.join(self.match_words) if self.match_words else '\nNo matches'
        separator = '-' * 30 + '\n'

        colored_source_name = {
            'Reuters.com': colorama.Back.RED + colorama.Fore.WHITE + 'Reuters.com' + colorama.Style.RESET_ALL,
            'BBC News': colorama.Back.RED + colorama.Fore.WHITE + 'BBC News' + colorama.Style.RESET_ALL,
            'Lenta.Ru': colorama.Back.MAGENTA + colorama.Fore.WHITE + 'Lenta.Ru' + colorama.Style.RESET_ALL,
            'РИА Новости': colorama.Back.BLUE + colorama.Fore.WHITE + 'РИА Новости' + colorama.Style.RESET_ALL
        }

        this_source_name = colored_source_name[
            self.source_name] if self.source_name in colored_source_name else self.source_name

        return '{6} - {5}{0} - {1} - {2} - {3}{4}\n'.format(this_source_name,
                                                            self.publish_date,
                                                            self.title,
                                                            self.source,
                                                            match_text,
                                                            separator,
                                                            self.id)

    def check_for_match(self, pattern):
        match = []
        if self.title:
            match += pattern.findall(self.title.lower())

        if self.text:
            match += pattern.findall(self.text.lower())

        if match:
            logger.info(
                '{0} - {1}: Match!!!'.format(self.id, self.source_name))
            self.match_words = tools.delete_duplicates(match)
            return True
        else:
            return False

    def get_article_body(self):
        return self.article_body

    def get_article_body_json(self):
        return json.dumps(self.article_body, ensure_ascii=False)
