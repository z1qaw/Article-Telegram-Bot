import time
import requests
import re

import article_checker
import worker
import database as db_api
import bot_config

import api.ria
import api.lenta
import api.bbc
import api.reuters

from bot import ArticleBot
from error import prepare_article_error

from yandex_translate import YandexTranslate


def test():
    bot_token = bot_config.bot_token
    database = db_api.Database(bot_config.database_url)

    yandex_translater = YandexTranslate(bot_config.yandex_api_key)

    translate = {
        'to': bot_config.main_language,
        'translate': True,
        'translator': yandex_translater,
        'translate_links': True
    }

    requests_session = requests.session()
    bot = ArticleBot(bot_token, database, requests_session, translate)

    bp = api.bbc.BbcParser(requests_session)
    rp = api.reuters.ReutersParser(requests_session)

    bt_article = article_checker.Article(bp.get_article('/news/uk-50067855'))
    bot.send_article(bt_article)



if __name__ == '__main__':
    test()
    input()
