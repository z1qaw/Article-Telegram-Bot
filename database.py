import psycopg2
import time

import bot_config
from error import prepare_article_error


class Database:
    def __init__(self, path, retry=True, max_retry=10):
        self.connection = psycopg2.connect(path, sslmode='require')
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        self.retry = retry
        self.max_retry = max_retry

    def check_table(self, table_name):
        for i in range(self.max_retry):
            try:
                self.cursor.execute("CREATE TABLE IF NOT EXISTS \"{0}\" (uri text)".format(table_name))
                break
            except Exception as error:
                prepare_article_error(error)
                time.sleep(0.3)

            if not self.retry:
                break

    def delete_table(self, table_name):
        for i in range(self.max_retry):
            try:
                self.cursor.execute("DROP TABLE IF EXISTS {0}".format(table_name))
                break
            except Exception as error:
                prepare_article_error(error)
                time.sleep(0.1)

            if not self.retry:
                break

    def check_user_table(self):
        for i in range(self.max_retry):
            try:
                self.cursor.execute("CREATE TABLE IF NOT EXISTS \"{0}\" (id integer, PRIMARY KEY (id))".format('users'))
                break
            except Exception as error:
                prepare_article_error(error)
                time.sleep(0.3)

            if not self.retry:
                break

    def insert_user_id(self, user_id):
        self.check_user_table()
        for i in range(self.max_retry):
            try:
                self.cursor.execute('INSERT INTO {0} (id) VALUES ({1})'.format('users', user_id))
                break
            except Exception as error:
                prepare_article_error(error)
                time.sleep(0.1)

            if not self.retry:
                break

    def is_user_exist(self, user_id):
        self.check_user_table()
        for i in range(self.max_retry):
            try:
                self.cursor.execute("SELECT COUNT(*) FROM {0} WHERE id = {1}".format('users', user_id))
                exists = self.cursor.fetchone()
                is_exists = True if exists[0] else False
                return is_exists
            except Exception as error:
                prepare_article_error(error)
                time.sleep(0.2)

            if not self.retry:
                break

    def delete_user_id(self, user_id):
        self.check_user_table()
        for i in range(self.max_retry):
            try:
                self.cursor.execute("DELETE FROM {0} WHERE id = {1}".format('users', user_id))
                break
            except Exception as error:
                prepare_article_error(error)
                time.sleep(0.2)

            if not self.retry:
                break

    def get_users_list(self):
        self.check_user_table()
        for i in range(self.max_retry):
            try:
                self.cursor.execute("SELECT * FROM {0}".format('users'))
                data = self.cursor.fetchall()

                ids = []
                for row in data:
                    ids.append(row[0])
                return ids
            except:
                time.sleep(0.2)

            if not self.retry:
                break

    def insert_uri(self, table_name, element):
        for i in range(self.max_retry):
            try:
                self.cursor.execute('INSERT INTO {0} (uri) VALUES (\'{1}\')'.format(table_name, element))
                break
            except Exception as error:
                prepare_article_error(error)
                time.sleep(0.1)

            if not self.retry:
                break

    def is_exist(self, table_name, element):
        for i in range(self.max_retry):
            try:
                self.cursor.execute("SELECT COUNT(*) FROM {0} WHERE uri = \'{1}\'".format(table_name, element))
                exists = self.cursor.fetchone()
                is_exists = True if exists[0] else False
                return is_exists
            except:
                time.sleep(0.2)

            if not self.retry:
                break

def main():
    db = Database(bot_config.database_url)

    while True:
        print(db.get_users_list())


if __name__ == '__main__':
    main()