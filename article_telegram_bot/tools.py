import os
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import cssutils
import requests

url_re = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'


def delete_duplicates(l: list) -> list:
    new_l = []
    for element in l:
        if element not in new_l:
            new_l.append(element)

    return new_l


def parse_css(css: str) -> dict:
    dct = {}
    sheet = cssutils.parseString(css)

    for rule in sheet:
        selector = rule.selectorText
        styles = rule.style.cssText
        dct[selector] = styles

    return dct


def delete_query(uri: str, query_name: str) -> str:
    parsed_url = urlparse(uri)
    url_query = parse_qs(parsed_url.query, keep_blank_values=True)
    url_query.pop(query_name, None)
    cleaned = urlunparse(parsed_url._replace(query=urlencode(url_query, True)))

    return cleaned


def dump_html(uri: str) -> None:
    with open('dumo.html', 'w', encoding='utf-8') as f:
        f.write(requests.get(uri).text)


def get_env_var(var_name: str, default: Any = None, required: bool = False) -> Any:
    value = os.environ.get(var_name, default=default)
    if not value and required:
        raise ValueError(
            f'You must specify environment variable named {var_name}. '
            'In Heroku go to App settings -> Config Vars -> Reveal Config Vars -> Add. '
            f'In Bash type \"export {var_name}=your_value\".'
        )

    return value
