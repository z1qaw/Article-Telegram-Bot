import threading
import time
from typing import List, Union

import psycopg2
from loguru import logger


def retry_on_error(f):
    def wrapper(*args):
        db_instanse = args[0]

        for i in range(db_instanse.max_retry):
            try:
                f(*args)
                break
            except Exception as error:
                logger.exception(error)
                time.sleep(0.3)

            if not db_instanse.retry:
                break

    return wrapper


class Database(threading.Thread):
    def __init__(self, path: str, retry: bool = True, max_retry: int = 10) -> None:
        super(Database, self).__init__()
        self.setDaemon(True)

        self.connection = psycopg2.connect(path, sslmode='require')
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        self.retry = retry
        self.max_retry = max_retry
        self.tables_overflow_check_time = 5 * 60
        self.checker_tables = []

    @retry_on_error
    def check_table(self, table_name: str) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS \"{table_name}\" (
                    id SERIAL PRIMARY KEY,
                    uri text,
                    add_time TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )'''
            )

    @retry_on_error
    def delete_table(self, table_name: str) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'DROP TABLE IF EXISTS {table_name}'
            )

    @retry_on_error
    def check_user_table(self) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS \"users\" (
                    id SERIAL PRIMARY KEY,
                    telegram_id integer,
                    add_time TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )"""
            )

    @retry_on_error
    def insert_user_id(self, user_id: Union[str, int]) -> None:
        self.check_user_table()
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'INSERT INTO users (telegram_id) VALUES ({user_id})')

    @retry_on_error
    def get_total_rows_count(self) -> Union[list, None]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'SELECT SUM(n_live_tup) FROM pg_stat_user_tables;')
            result = cursor.fetchone()
            return result

    @retry_on_error
    def is_user_exist(self, user_id: Union[str, int]) -> Union[bool, None]:
        self.check_user_table()
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'SELECT COUNT(*) FROM users WHERE telegram_id = {user_id}'
            )
            exists = cursor.fetchone()
            is_exists = True if exists[0] else False
            return is_exists

    @retry_on_error
    def delete_user_id(self, user_id: Union[str, int]) -> None:
        self.check_user_table()
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'DELETE FROM users WHERE telegram_id = {user_id}'
            )

    @retry_on_error
    def get_users_list(self) -> Union[List[str], None]:
        self.check_user_table()
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users')
            data = cursor.fetchall()

            ids = []
            for row in data:
                ids.append(row[1])
            return ids

    @retry_on_error
    def insert_uri(self, table_name: str, uri: str) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'INSERT INTO {table_name} (uri) VALUES (\'{uri}\')'
            )

    @retry_on_error
    def is_exist(self, table_name: str, uri: str) -> Union[bool, None]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'SELECT COUNT(*) FROM {table_name} WHERE uri = \'{uri}\''
            )
            exists = cursor.fetchone()
            is_exists = True if exists[0] else False
            return is_exists

    def run(self) -> None:
        while True:
            for table in self.checker_tables:
                limit = table['normal_overflow_count']
                table_name = table['table_name']

                self.check_table(table_name)

                with self.connection.cursor() as cursor:
                    query = f"""
                        DELETE FROM {table_name} WHERE id NOT IN (
                            SELECT id FROM {table_name} ORDER BY add_time DESC LIMIT {limit});"""
                    cursor.execute(query)
                    deleted_rows_count = cursor.rowcount
                    time.sleep(1)
                    logger.info(
                        f'{self.__class__.__name__}: Clear rows in table {table_name} '
                        f'except of {limit} last rows. {deleted_rows_count} deleted.')
                    total_rows_count = int(self.get_total_rows_count()[0])
                    logger.info(
                        f'{self.__class__.__name__}: Total rows count: {total_rows_count}')
            time.sleep(self.tables_overflow_check_time)
