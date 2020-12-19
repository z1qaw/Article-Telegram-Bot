import psycopg2
import time
import threading
from loguru import logger
from . import bot_config


class Database(threading.Thread):
    def __init__(self, path, retry=True, max_retry=10):
        self.connection = psycopg2.connect(path, sslmode='require')
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        self.retry = retry
        self.max_retry = max_retry

    def check_table(self, table_name):
        for i in range(self.max_retry):
            try:
                self.cursor.execute(
                    f'''CREATE TABLE IF NOT EXISTS \"{table_name}\" (
                           id SERIAL PRIMARY KEY,
                           uri text,
                           add_time TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )'''
                )
                break
            except Exception as error:
                logger.exception(error)
                time.sleep(0.3)

            if not self.retry:
                break

    def delete_table(self, table_name):
        for i in range(self.max_retry):
            try:
                self.cursor.execute(
                    f'DROP TABLE IF EXISTS {table_name}'
                )
                break
            except Exception as error:
                logger.exception(error)
                time.sleep(0.1)

            if not self.retry:
                break

    def check_user_table(self):
        for i in range(self.max_retry):
            try:
                self.cursor.execute(
                    """CREATE TABLE IF NOT EXISTS \"users\" (
                           id SERIAL PRIMARY KEY,
                           telegram_id integer,
                           add_time TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )"""
                )
                break
            except Exception as error:
                logger.exception(error)
                time.sleep(0.3)

            if not self.retry:
                break

    def insert_user_id(self, user_id):
        self.check_user_table()
        for i in range(self.max_retry):
            try:
                self.cursor.execute(
                    f'INSERT INTO users (telegram_id) VALUES ({user_id})')
                break
            except Exception as error:
                logger.exception(error)
                time.sleep(0.1)

            if not self.retry:
                break

    def is_user_exist(self, user_id):
        self.check_user_table()
        for i in range(self.max_retry):
            try:
                self.cursor.execute(
                    f'SELECT COUNT(*) FROM users WHERE telegram_id = {user_id}'
                )
                exists = self.cursor.fetchone()
                is_exists = True if exists[0] else False
                return is_exists
            except Exception as error:
                logger.exception(error)
                time.sleep(0.2)

            if not self.retry:
                break

    def delete_user_id(self, user_id):
        self.check_user_table()
        for i in range(self.max_retry):
            try:
                self.cursor.execute(
                    f'DELETE FROM users WHERE telegram_id = {user_id}'
                )
                break
            except Exception as error:
                logger.exception(error)
                time.sleep(0.2)

            if not self.retry:
                break

    def get_users_list(self):
        self.check_user_table()
        for i in range(self.max_retry):
            try:
                self.cursor.execute('SELECT * FROM users')
                data = self.cursor.fetchall()

                ids = []
                for row in data:
                    ids.append(row[1])
                return ids
            except:
                time.sleep(0.2)

            if not self.retry:
                break

    def insert_uri(self, table_name, uri):
        for i in range(self.max_retry):
            try:
                self.cursor.execute(
                    f'INSERT INTO {table_name} (uri) VALUES (\'{uri}\')'
                )
                break
            except Exception as error:
                logger.exception(error)
                time.sleep(0.1)

            if not self.retry:
                break

    def is_exist(self, table_name, uri):
        for i in range(self.max_retry):
            try:
                self.cursor.execute(
                    f'SELECT COUNT(*) FROM {table_name} WHERE uri = \'{uri}\''
                )
                exists = self.cursor.fetchone()
                is_exists = True if exists[0] else False
                return is_exists
            except:
                time.sleep(0.2)

            if not self.retry:
                break

    def start():
        pass
