import threading
import time

from . import article_checker
from . import tools

from loguru import logger


class CheckerThread(threading.Thread):
    def __init__(self, parser, queue, database, database_table_name, timeout):
        super(CheckerThread, self).__init__()
        self.setDaemon(True)

        self.database = database
        self.database_table_name = database_table_name
        self.parser = parser
        self.timeout = timeout
        self.queue = queue

        logger.info(f'{self.parser.__class__.__name__} thread initialized')

    def run(self):
        logger.info('Checker thread started')
        while True:
            try:
                while True:
                    last_info = tools.delete_duplicates(
                        self.parser.get_latest())
                    for uri in last_info:
                        self.database.check_table(self.database_table_name)
                        if not self.database.is_exist(self.database_table_name, uri):
                            this_article = self.parser.get_article(uri)
                            self.database.insert_uri(
                                self.database_table_name, uri)
                            if this_article:
                                this_article = article_checker.Article(
                                    this_article)
                                self.queue.append(this_article)
                        time.sleep(1)

                    time.sleep(self.timeout)
            except Exception as error:
                logger.exception(
                    f'Error... Reload worker thread for {self.parser.__class__.__name__} after 15 seconds..')
                time.sleep(15)


class ArticleQueueThread(threading.Thread):
    def __init__(self, telegram_bot, parsers_settings):
        super(ArticleQueueThread, self).__init__()
        self.setDaemon(True)

        self.queue = []
        self.telegram_bot = telegram_bot
        self.parsers_settings = parsers_settings

        print('Queue thread: Initialized')

    def append(self, article):
        self.queue.append(article)

    def get(self):
        if len(self.queue) > 0:
            article = self.queue[0]
            del self.queue[0]
            return article

    def run(self):
        print('Queue thread: Started')
        while True:
            if len(self.queue) > 0:
                last_article = self.get()
                last_article.send_key_words = self.parsers_settings[
                    last_article.source_name]['send_key_words']
                if last_article.check_for_match(self.parsers_settings[last_article.source_name]['key_words']):
                    try:
                        self.telegram_bot.send_article(last_article)
                    except Exception as error:
                        prepare_article_error(error)
            time.sleep(1)


class BotPollingThread(threading.Thread):
    def __init__(self, article_bot, database, password):
        super(BotPollingThread, self).__init__()
        self.setDaemon(True)

        self.bot = article_bot.bot
        self.database = database
        self.password = password

    def run(self):
        @self.bot.message_handler(commands=['my_id'])
        def send_id(message):
            print('Bot: Message from {0}: {1}'.format(
                message.chat.id, message.text))
            self.bot.send_message(message.chat.id, str(message.chat.id))

        @self.bot.message_handler(commands=['start'])
        def send_start(message):
            print('Bot: Message from {0}: {1}'.format(
                message.chat.id, message.text))
            text = 'Hello!'
            self.bot.reply_to(message, text)
            print('Bot: Send text to {0}: {1}'.format(message.chat.id, text))

        @self.bot.message_handler(commands=['subscribe'])
        def add_user(message):
            print('Bot: Message from {0}: {1}'.format(
                message.chat.id, message.text))
            user_id = message.chat.id
            is_password = self.password
            if not is_password:
                if not self.database.is_user_exist(user_id):
                    text = 'Теперь вы получатель. Вы будете получать новые статьи в этом чате.'
                    self.database.insert_user_id(user_id)
                    print('Bot: Insert user {0}'.format(user_id))
                    print('Bot: Send text to {0}: {1}'.format(user_id, text))

                    self.bot.reply_to(message, text)
                else:
                    text = 'Вы уже получатель.'
                    print('Bot: Send text to {0}: {1}'.format(user_id, text))
                    self.bot.reply_to(message, text)
            elif self.database.is_user_exist(user_id):
                self.bot.reply_to(message, 'Вы уже получатель.')
            else:
                self.bot.reply_to(message, 'Упс! Пришлите пароль.')

        @self.bot.message_handler(commands=['stop'])
        def delete_user(message):
            print('Bot: Message from {0}: {1}'.format(
                message.chat.id, message.text))
            user_id = message.chat.id
            if self.database.is_user_exist(user_id):
                text = 'Теперь вы не будете получать новые статьи. Чтобы снова получать их, снова подпишитесь через команду /subscribe.'
                self.database.delete_user_id(user_id)
                print('Bot: Delete user {0}'.format(user_id))
                print('Bot: Send text to {0}: {1}'.format(user_id, text))

                self.bot.reply_to(message, text)
            else:
                text = 'Вы не являетесь получателем.'
                print('Bot: Send text to {0}: {1}'.format(user_id, text))
                self.bot.reply_to(message, text)

        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):
            print('Bot: (message_handler) Message from {0}: {1}'.format(
                message.chat.id, message.text))
            if message.text == self.password:
                if not self.database.is_user_exist(message.chat.id):
                    user_id = message.chat.id
                    self.database.insert_user_id(user_id)
                    self.bot.reply_to(
                        message, 'Теперь вы получатель. Вы будете получать новые статьи в этом чате.')
                else:
                    self.bot.reply_to(message, 'Вы уже получатель.')

        self.bot.polling(timeout=0.2)
