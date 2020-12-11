import time

import requests
import telebot

from . import tools
from . import bot_config

from telebot import apihelper
from io import BytesIO
from telebot.types import InputMediaPhoto
import urllib.parse

from loguru import logger

if bot_config.use_proxy:
    logger.info('Bot use proxy.')
    apihelper.proxy = bot_config.proxies


class ArticleBot:
    def __init__(self, token, database, requests_session, translate):
        self.bot = telebot.TeleBot(token)
        self.requests_session = requests_session
        self.translate = translate['translate']
        self.translate_language = translate['to']
        self.translator = translate['translator']
        self.translate_links = translate['translate_links']
        self.database = database

    def send_article(self, article):
        current_users = self.database.get_users_list()
        if not current_users:
            return 1
        logger.info(current_users)

        logger.info(
            'Bot: {0} - Try to send article to all users...'.format(article.id))
        images_to_send = []

        for image_link in tools.delete_duplicates([article.main_image_link] + article.article_images):
            if image_link:
                try:
                    try:
                        response = self.requests_session.get(image_link)
                    except requests.exceptions.SSLError:
                        response = self.requests_session.get(
                            image_link, verify=False)
                    if response.status_code == 200:
                        if len(response.content) > 0:
                            img_bytes = BytesIO(response.content)
                            images_to_send.append(InputMediaPhoto(img_bytes))
                except Exception as error:
                    logger.exception(error)
                time.sleep(0.2)

        translated = {'article_title': None,
                      'article_text': None}

        if (article.text or article.title) and (article.language != self.translate_language) and self.translate:
            if article.title:
                try:
                    translated['article_title'] = self.translator.translate(article.title,
                                                                            '-'.join([article.language,
                                                                                      self.translate_language]))[
                        'text'][0]
                except Exception as error:
                    logger.warning(
                        'Can"t translate text using Yandex.Translate')
            if article.text:
                try:
                    translated['article_text'] = self.translator.translate(article.text,
                                                                           '-'.join([article.language,
                                                                                     self.translate_language]))['text'][
                        0]
                except Exception as error:
                    logger.warning(
                        'Can"t translate text using Yandex.Translate')

        if not self.translate or (article.language == self.translate_language):
            article_title = article.title
            article_text = article.text
        else:
            article_title = translated['article_title'] if translated['article_title'] else article.title
            article_text = translated['article_text'] if translated['article_text'] else article.text

        text = 'Источник: {2} {3}\n\nДата публикации: {1}\n\n{0}\n\n{4}'.format(article_title,
                                                                                article.publish_date,
                                                                                article.source_name,
                                                                                article.source,
                                                                                article_text)

        translate_link = 'https://translate.google.com/?source=gtx_c#view=home&op=translate&sl={0}&tl={1}&text={2}'.format(
            article.language, self.translate_language, urllib.parse.quote(
                article.source)
        )
        translate_link_text = '[Перевод статьи на Google Translate]({0})'.format(
            translate_link)

        re_text = 'Ключевые слова:\n' + \
            (', '.join(article.match_words)
             if article.match_words else "Не обнаружено.")

        is_forward = False
        message_to_forward = None

        for user_id in current_users:
            try:
                self.bot.send_chat_action(user_id, 'typing')
            except telebot.apihelper.ApiTelegramException:
                current_users.remove(user_id)
                continue

            logger.debug(
                'Bot: User {0} - {1} - Try to send separator...'.format(str(user_id), article.id))
            self.bot.send_message(user_id, '-' * 10)
            logger.info(
                'Bot: User {0} - {1} -  Separator sented'.format(str(user_id), article.id))

            if article.send_key_words:
                logger.info(
                    'Bot: User {0} - {1} - Try to send key words...'.format(str(user_id), article.id))
                self.bot.send_message(user_id, re_text)
                logger.info(
                    'Bot: User {0} - {1} -  Key words sented'.format(str(user_id), article.id))

            if self.translate_links and (article.language != self.translate_language):
                logger.info(
                    'Bot: User {0} - {1} - Try to send translate link...'.format(str(user_id), article.id))
                self.bot.send_message(
                    user_id, translate_link_text, disable_web_page_preview=True, parse_mode='Markdown')
                logger.info(
                    'Bot: User {0} - {1} -  Translate link sented'.format(str(user_id), article.id))

            if len(text) > 4096:
                message_part = 0
                for x in range(0, len(text), 4096):
                    try:
                        logger.info(
                            'Bot: User {0} - {1} - Try to send text message part...'.format(str(user_id), article.id))
                        self.bot.send_message(user_id, text[x:x + 4096],
                                              disable_web_page_preview=True)
                        logger.info(
                            'Bot: User {0} - {1} - Message part sented'.format(str(user_id), article.id))
                    except Exception as error:
                        logger.exception(error)

                    message_part += 1
            else:
                try:
                    logger.info(
                        'Bot: User {0} - {1} - Try to send full text message...'.format(str(user_id), article.id))
                    self.bot.send_message(
                        user_id, text, disable_web_page_preview=True)
                    logger.info(
                        'Bot: User {0} - {1} - Message sented'.format(str(user_id), article.id))
                except Exception as error:
                    logger.exception(error)

                self.bot.send_chat_action(user_id, 'upload_photo')

            if not is_forward:
                is_forward = True
                if images_to_send:
                    logger.info(
                        'Bot: User {0} - {1} - Try to send photos'.format(str(user_id), article.id))
                    try:
                        message_to_forward = self.bot.send_media_group(
                            user_id, images_to_send)
                        logger.info(
                            'Bot: User {0} - {1} - Photos sented'.format(str(user_id), article.id))
                    except Exception as error:
                        logger.exception(error)
            else:
                try:
                    logger.info(
                        'Bot: User {0} - {1} - Try to send photos'.format(str(user_id), article.id))
                    self.bot.send_media_group(user_id,
                                              [InputMediaPhoto(
                                                  image.photo[0].file_id) for image in message_to_forward])
                    logger.info(
                        'Bot: User {0} - {1} - Photos sented'.format(str(user_id), article.id))
                except Exception as error:
                    logger.exception(error)
