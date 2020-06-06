import cssutils

from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

import requests

url_re = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'


def delete_duplicates(l):
    new_l = []
    for element in l:
        if element not in new_l:
            new_l.append(element)

    return new_l


def parse_css(css):
    dct = {}
    sheet = cssutils.parseString(css)

    for rule in sheet:
        selector = rule.selectorText
        styles = rule.style.cssText
        dct[selector] = styles

    return dct


def delete_query(uri, query_name):
    parsed_url = urlparse(uri)
    url_query = parse_qs(parsed_url.query, keep_blank_values=True)
    url_query.pop(query_name, None)
    cleaned = urlunparse(parsed_url._replace(query=urlencode(url_query, True)))
    return cleaned


def dump_html(uri):
    with open('dumo.html', 'w', encoding='utf-8') as f:
        f.write(requests.get(uri).text)
