from bs4 import BeautifulSoup
from requests import Session
from datetime import datetime


def get_html_soup_by_url(session: Session, url: str, request_headers: dict = None, verify=True):
    if request_headers:
        response = session.get(url, headers=request_headers, verify=verify)
    else:
        response = session.get(url, verify=verify)
    response_html = response.content.decode()
    return BeautifulSoup(response_html, 'html.parser')


def parse_iso_8601_time(time: str):
    return datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ").strftime('%d.%m.%Y %H:%M:%S')
