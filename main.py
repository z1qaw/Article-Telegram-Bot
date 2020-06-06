import time
import requests
import urllib3

import worker
import database as db_api
import bot_config

import api.ria
import api.lenta
import api.bbc
import api.reuters
import api.tourprom
import api.ru_euronews
import api.inosmi
import api.iransegodnya
import api.arabianbusiness
import api.sana
import api.sana_ru
import api.nna
import api.y_oman
import api.yenisafak

from bot import ArticleBot
from error import prepare_article_error

from yandex_translate import YandexTranslate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    print('\n\n')
    print('-' * 20)
    print('Article Telegram Bot [HEROKU EDITION]', '\n')
    print('Try to set up...')

    bot_token = bot_config.bot_token
    database = db_api.Database(bot_config.database_url)

    yandex_translater = YandexTranslate(bot_config.yandex_api_key)

    translate = {
        'to': bot_config.main_language,
        'translate': True,
        'translate_links': True,
        'translator': yandex_translater
    }

    requests_session = requests.session()
    bot = ArticleBot(bot_token, database, requests_session, translate)
    bot_polling_thread = worker.BotPollingThread(bot, database, bot_config.user_secret)

    parsers_settings = bot_config.parsers
    parsers_names = {
        'РИА Новости': api.ria.RiaParser,
        'Reuters.com': api.reuters.ReutersParser,
        'Ru EuroNews': api.ru_euronews.RuEuronewsParser,
        'TourProm.ru': api.tourprom.TourpromParser,
        'Lenta.Ru': api.lenta.LentaParser,
        'InoSmi': api.inosmi.InoSmiParser,
        'BBC News': api.bbc.BbcParser,
        'IranToday': api.iransegodnya.IranTodayParser,
        'Arabian Business News': api.arabianbusiness.ArabianBusinessParser,
        'Sana News EN': api.sana.SanaParser,
        'Sana News RU': api.sana_ru.RuSanaParser,
        'NNA News': api.nna.NnaParser,
        'Y-Oman News': api.y_oman.YOmanParser,
        'YeniSafak News': api.yenisafak.YeniSafakParser,
    }

    article_queue_thread = worker.ArticleQueueThread(bot, parsers_settings)
    checker_threads = []

    for key in parsers_settings:
        if not parsers_settings[key]['use']:
            continue
        parser = parsers_names[key](requests_session)
        checker_threads.append(worker.CheckerThread(parser, article_queue_thread, database, parser.db_table_name,
                                                    bot_config.parse_timeout))
        time.sleep(0.5)

    bot_polling_thread.start()
    article_queue_thread.start()
    for checker_thread in checker_threads:
        checker_thread.start()
        time.sleep(0.5)

    bot_polling_thread.join()
    article_queue_thread.join()
    for checker_thread in checker_threads:
        checker_thread.join()
        time.sleep(0.5)
    print('\nAll threads has been initialized')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('KeyboardInterrupt: exit script.')
    except Exception as error:
        prepare_article_error(error)
