import urllib.parse
from typing import Union

from loguru import logger
from requests import Session
from telebot import TeleBot, apihelper
from telebot.types import InputMediaPhoto

from . import bot_config, tools
from .article_checker import Article
from .database import Database

if bot_config.use_proxy:
    logger.info('Bot use proxy.')
    apihelper.proxy = bot_config.proxies


class ArticleBot:
    def __init__(self, token: str, database: Database, requests_session: Session, translate: dict) -> None:
        self.bot = TeleBot(token)
        self.requests_session = requests_session
        self.translate = translate['translate']
        self.translate_language = translate['to']
        self.translator = translate['translator']
        self.translate_links = translate['translate_links']
        self.database = database

    def _send_separator(self, chat_id: Union[int, str], article_id: str) -> None:
        logger.debug(
            'Bot: User {0} - {1} - Try to send separator...'.format(str(chat_id), article_id))
        self.bot.send_message(chat_id, '-' * 10)
        logger.info(
            'Bot: User {0} - {1} -  Separator sented'.format(str(chat_id), article_id))

    def _send_article_keywords(self, chat_id: Union[int, str],
                               article_match_words: list[str], article_id: str) -> None:
        re_text = 'Ключевые слова:\n' + \
            (', '.join(article_match_words)
                if article_match_words else "Не обнаружено.")

        logger.info(
            'Bot: User {0} - {1} - Try to send key words...'.format(str(chat_id), article_id))
        self.bot.send_message(chat_id, re_text)
        logger.info(
            'Bot: User {0} - {1} -  Key words sented'.format(str(chat_id), article_id))

    def _send_article_translate_link(self, chat_id: Union[int, str], article_id: str,
                                     article_language: str, article_source: str
                                     ) -> None:
        translate_link = 'https://translate.google.com/?source=gtx_c#view=home&op=translate&sl={0}&tl={1}&text={2}'.format(
            article_language,
            self.translate_language,
            urllib.parse.quote(article_source)
        )
        translate_link_text = f'[Перевод статьи на Google Translate]({translate_link})'

        logger.info(
            'Bot: User {0} - {1} - Try to send translate link...'.format(str(chat_id), article_id))
        self.bot.send_message(
            chat_id, translate_link_text, disable_web_page_preview=True, parse_mode='Markdown')
        logger.info(
            'Bot: User {0} - {1} -  Translate link sented'.format(str(chat_id), article_id))

    def _send_full_article_text(self, chat_id: Union[int, str], article_id: str, text: str) -> None:
        try:
            logger.info(
                'Bot: User {0} - {1} - Try to send full text message...'.format(str(chat_id), article_id))
            self.bot.send_message(
                chat_id, text, disable_web_page_preview=True)
            logger.info(
                'Bot: User {0} - {1} - Message sented'.format(str(chat_id), article_id))
        except Exception as error:
            logger.exception(error)

    def _send_big_message_parts(self, chat_id: Union[int, str], article_id: str, text: str) -> None:
        message_part = 0
        for x in range(0, len(text), 4096):
            try:
                logger.info(
                    'Bot: User {0} - {1} - Try to send text message part...'.format(str(chat_id), article_id))
                self.bot.send_message(
                    chat_id,
                    text[x:x + 4096],
                    disable_web_page_preview=True
                )
                logger.info(
                    'Bot: User {0} - {1} - Message part sented'.format(str(chat_id), article_id))
            except Exception as error:
                logger.exception(error)

            message_part += 1

    def _send_article_images(self, chat_id: Union[str, int], article_id: str,
                             images_group: list[InputMediaPhoto], forward: bool,
                             forward_images_message: Union[None, list] = None
                             ) -> Union[list, None]:
        try:
            if not forward:
                logger.info(
                    'Bot: User {0} - {1} - Try to send photos'.format(str(chat_id), article_id))
                message_to_forward = self.bot.send_media_group(
                    chat_id, images_group)
                logger.info(
                    'Bot: User {0} - {1} - Photos sented'.format(str(chat_id), article_id))
                return message_to_forward
            else:
                logger.info(
                    'Bot: User {0} - {1} - Try to send photos'.format(str(chat_id), article_id))
                self.bot.send_media_group(
                    chat_id,
                    [InputMediaPhoto(image.photo[0].file_id)
                        for image in forward_images_message]
                )
                logger.info(
                    'Bot: User {0} - {1} - Photos sented'.format(str(chat_id), article_id))
                return None

        except Exception as error:
            logger.exception(error)

    def _translate_article_text(self, article: Article) -> dict:
        translated = {
            'article_title': None,
            'article_text': None
        }

        if (article.text or article.title) and (article.language != self.translate_language) and self.translate:
            try:
                if article.title:
                    translated['article_title'] = self.translator.translate(
                        article.title,
                        '-'.join([article.language, self.translate_language]))['text'][0]
                if article.text:
                    translated['article_text'] = self.translator.translate(
                        article.text,
                        '-'.join(
                            [article.language, self.translate_language])
                    )['text'][0]
            except:
                logger.warning(
                    'Can"t translate text using Yandex.Translate')

        return translated

    def send_article(self, article: Article) -> int:
        current_users = self.database.get_users_list()
        if not current_users:
            return 1

        logger.info(
            'Bot: {0} - Try to send article to all users...'.format(article.id))
        images_to_send = []

        for image_link in tools.delete_duplicates([article.main_image_link] + article.article_images)[:7]:
            if image_link:
                images_to_send.append(InputMediaPhoto(image_link))

        translated = self._translate_article_text(article)

        if not self.translate or (article.language == self.translate_language):
            article_title = article.title
            article_text = article.text
        else:
            article_title = translated['article_title'] or article.title
            article_text = translated['article_text'] or article.text

        text = 'Источник: {2} {3}\n\nДата публикации: {1}\n\n{0}\n\n{4}'.format(
            article_title,
            article.publish_date,
            article.source_name,
            article.source,
            article_text
        )

        is_forward = False
        message_to_forward = None

        for user_id in current_users:
            try:
                self.bot.send_chat_action(user_id, 'typing')
            except apihelper.ApiTelegramException:
                current_users.remove(user_id)
                logger.warning(
                    'Bot: User {user_id} has been removed from subs')
                continue

            self._send_separator(chat_id=user_id, article_id=article.id)

            if article.send_key_words:
                self._send_article_keywords(chat_id=user_id, article_match_words=article.match_words,
                                            article_id=article.id)

            if self.translate_links and (article.language != self.translate_language):
                self._send_article_translate_link(
                    chat_id=user_id, article_id=article.id, article_language=article.language,
                    article_source=article.source)

            if len(text) > 4096:
                self._send_big_message_parts(
                    chat_id=user_id, article_id=article.id, text=text)
            else:
                self._send_full_article_text(
                    chat_id=user_id, article_id=article.id, text=text)
            if images_to_send:
                self.bot.send_chat_action(user_id, 'upload_photo')

                if not is_forward:
                    is_forward = True
                    message_to_forward = self._send_article_images(chat_id=user_id, article_id=article.id,
                                                                   images_group=images_to_send, forward=False)
                else:
                    self._send_article_images(chat_id=user_id, article_id=article.id, images_group=images_to_send,
                                              forward=True, forward_images_message=message_to_forward)

        return 0
