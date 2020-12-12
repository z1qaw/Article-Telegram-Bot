"""
Это конфигурационный файл для Article Telegram Bot.
Заполните поля ниже перед тем, как запускать бота через main.py!
"""

# "bot_token" - Токен для бота. Можно получить в Telegram, создав бота в @BotFather
import re

bot_token = "1202191308:AAFR1oltwd9QozwXoei25e6xVHU6NuvTPNE"


# "user_secret" - пароль для добавления текущего пользователя в список получателей.
# Отправьте его боту, чтобы добавить текущего пользователя.
# Поставьте значение None, чтобы выключить защиту и включить команду /subscribe
user_secret = None


# "database_uri" - ссылка на базу данных Heroku Postgres.
database_url = "postgres://osafddrzqqyzlj:24085bd158ae9e516c622ba36b582f355050a2d1c844d89d6d1cec87ade17a5c@ec2-3-248-4-172.eu-west-1.compute.amazonaws.com:5432/d5nq1armneg9ml"


# "key_words" - ключевые слова.
regular_key_words = r'азербайджан|\bбахрейн|\bегипет|\bегипт|\bизраил|\bиордани|\bирак|\bиран|\bйемен|\bкатар|\bкипр|\bкувейт|\bливан|арабски\w+ эмират\w+|\bоаэ|\bоман|\bпалестин|\bсаудовск\w+ арави\w+|\bсири\w+|\bтурци+|\bazerbaijan|armenia|bahrain|egypt|georgia|israel|jordan|iraq|\biran|yemen|qatar|cyprus|kuwait|lebanon|united arab emirates|UAE|\boman|palestine|saudi arabia|syria|turkey'
parsers = {
    'РИА Новости': {
        'key_words': re.compile(regular_key_words),
        'send_key_words': True,
        'use': True
    },
    'Reuters.com': {
        'key_words': re.compile('.*'),
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
        'use': True
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
}

# "main_language" - язык, на который будет переведён текст статьи.
# "translate" - переводить ли статьи на язык "main_language". True или False.
# Для перевода требуется API Ключ Yandex. Его можно получить на странице https://translate.yandex.com/developers/keys
yandex_api_key = 'trnsl.1.1.20180720T160118Z.e4138f77914a269e.d1e1a941a48bd5759f638178ffb2315567621cfb'
main_language = 'ru'
translate = True

# "parse_timeout" - переодичность, с которой бот проверяет сайты (в секундах). Рекомендуется указать от 30 секунд.
parse_timeout = 5

# "use_proxy" - использовать ли прокси для обхода блокировки Telegram в РФ (имеет только 2 значения: True - да, или False - нет).
# Рекомендуется использовать Tor Bundle proxy как бесплатный, стабильный и наиболее безопасный вариант.
# "proxies" преднастроена для использования Tor Bundle proxy.
# Heroku не требует прокси (пока что), поэтому при деплое на Heroku ставим False, иначе бот не запустится.
use_proxy = False
proxies = {
    "https": "socks5://127.0.0.1:9050"
}
