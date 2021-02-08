import sys

import requests
import urllib3
from loguru import logger
from yandex_translate import YandexTranslate

from . import bot_config
from . import database as db_api
from . import worker
from .api.services import (arabianbusiness, bbc, inosmi, iransegodnya, lenta, nna,
                           reuters, ria, ru_euronews, sana, sana_ru, tourprom,
                           yenisafak, arabnews, egyptianstreets, egypttoday, mehrnews,
                           qatarliving)
from .bot import ArticleBot

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    """ App Entry point"""
    logger.remove()
    logger.add(
        sys.stderr, format="{time} [{level}] {message}", level="INFO", colorize=True)

    logger.info('-' * 20)
    logger.info('Article Telegram Bot [HEROKU EDITION]', '\n')
    logger.info('Try to set up...')

    bot_token = bot_config.bot_token
    database = db_api.Database(bot_config.database_url)

    yandex_translater = YandexTranslate(bot_config.yandex_api_key or 'EMPTY')

    translate = {
        'to': bot_config.main_language,
        'translate': True,
        'translate_links': True,
        'translator': yandex_translater
    }

    requests_session = requests.session()
    bot = ArticleBot(bot_token, database, requests_session, translate)
    bot_polling_thread = worker.BotPollingThread(
        bot, database, bot_config.user_secret
    )

    parsers_settings = bot_config.parsers
    parsers_names = {
        'РИА Новости': ria.RiaParser,
        'Reuters.com': reuters.ReutersParser,
        'Ru EuroNews': ru_euronews.RuEuronewsParser,
        'TourProm.ru': tourprom.TourpromParser,
        'Lenta.Ru': lenta.LentaParser,
        'InoSmi': inosmi.InoSmiParser,
        'BBC News': bbc.BbcParser,
        'IranToday': iransegodnya.IranTodayParser,
        'Arabian Business News': arabianbusiness.ArabianBusinessParser,
        'Sana News EN': sana.SanaParser,
        'Sana News RU': sana_ru.RuSanaParser,
        'NNA News': nna.NnaParser,
        'YeniSafak News': yenisafak.YeniSafakParser,
        'EgyptianStreets News': egyptianstreets.EgyptianStreetsParser,
        'QatarLiving News': qatarliving.QatarLivingParser,
        'MehrNews': mehrnews.MehrNewsParser,
        'ArabNews': arabnews.ArabNewsParser,
        'EgyptToday News': egypttoday.EgyptTodayParser
    }

    article_queue_thread = worker.ArticleQueueThread(bot, parsers_settings)
    checker_threads = []

    for key in parsers_settings:
        if not parsers_settings[key]['use']:
            continue
        parser = parsers_names[key](requests_session)
        database.checker_tables.append(
            {
                'table_name': parser.db_table_name,
                'normal_overflow_count': parser.database_rows_overflow_count
            }
        )
        checker_threads.append(worker.CheckerThread(parser, article_queue_thread, database, parser.db_table_name,
                                                    bot_config.parse_interval))

    database.start()
    bot_polling_thread.start()
    article_queue_thread.start()
    for checker_thread in checker_threads:
        checker_thread.start()

    bot_polling_thread.join()
    article_queue_thread.join()
    for checker_thread in checker_threads:
        checker_thread.join()

    logger.info('All threads has been initialized')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt: exit script.')
