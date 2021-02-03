"""
Это конфигурационный файл для Article Telegram Bot.
Заполните поля ниже перед тем, как запускать бота через main.py!
"""

# "bot_token" - Токен для бота. Можно получить в Telegram, создав бота в @BotFather
import re
import os


bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')


# "user_secret" - пароль для добавления текущего пользователя в список получателей.
# Отправьте его боту, чтобы добавить текущего пользователя.
# Поставьте значение None, чтобы выключить защиту и включить команду /subscribe
user_secret = os.environ.get('SUBSCRIBE_SECRET')


# "database_uri" - ссылка на базу данных Heroku Postgres.
# database_url = "postgres://ypthpmtwdeankn:9cb0150e60d60a424680096fea2f6e6c6a178678c4178a92cae6aa2aaf44df13@ec2-54-217-204-34.eu-west-1.compute.amazonaws.com:5432/d1n8ob18he4jts"
database_url = os.environ.get('DATABASE_URL')

# "key_words" - ключевые слова.
regular_key_words = os.environ.get('REGULAR_KEYWORDS')
parsers = {
    'РИА Новости': {
        'key_words': re.compile(regular_key_words),
        'send_key_words': True,
        'use': True
    },
    'Reuters.com': {
        'key_words': re.compile(re.compile(regular_key_words)),
        'send_key_words': True,
        'use': True
    },
    'Ru EuroNews': {
        'key_words': re.compile(regular_key_words),
        'send_key_words': True,
        'use': True
    },
    'TourProm.ru': {
        'key_words': re.compile(regular_key_words),
        'send_key_words': True,
        'use': True
    },
    'Lenta.Ru': {
        'key_words': re.compile(regular_key_words),
        'send_key_words': True,
        'use': True
    },
    'InoSmi': {
        'key_words': re.compile(regular_key_words),
        'send_key_words': True,
        'use': True
    },
    'BBC News': {
        'key_words': re.compile(regular_key_words),
        'send_key_words': True,
        'use': True
    },
    'IranToday': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': True
    },
    'Arabian Business News': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': False
    },
    'Sana News EN': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': True
    },
    'Sana News RU': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': True
    },
    'NNA News': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': False
    },
    'Y-Oman News': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': False
    },
    'YeniSafak News': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': True
    },
    'EgyptianStreets News': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': True
    },
    'QatarLiving News': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': True
    },
    'MehrNews': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': True
    },
    'ArabNews': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': True
    },
    'EgyptToday News': {
        'key_words': re.compile('.*'),
        'send_key_words': False,
        'use': True
    },
}

# "main_language" - язык, на который будет переведён текст статьи.
# "translate" - переводить ли статьи на язык "main_language". True или False.
# Для перевода требуется API Ключ Yandex. Его можно получить на странице https://translate.yandex.com/developers/keys
yandex_api_key = os.environ.get('YANDEX_TRANSLATE_API_KEY')
main_language = 'ru'
translate = False

# "parse_interval" - переодичность, с которой бот проверяет сайты (в секундах). Рекомендуется указать от 30 секунд.
parse_interval = int(os.environ.get('PARSE_INTERVAL'))

# "use_proxy" - использовать ли прокси для обхода блокировки Telegram в РФ (имеет только 2 значения: True - да, или False - нет).
# Рекомендуется использовать Tor Bundle proxy как бесплатный, стабильный и наиболее безопасный вариант.
# "proxies" преднастроена для использования Tor Bundle proxy.
# Heroku не требует прокси (пока что), поэтому при деплое на Heroku ставим False, иначе бот не запустится.
use_proxy = False
proxies = {
    "https": "socks5://127.0.0.1:9050"
}
