from bs4 import BeautifulSoup
from requests import Session


def get_html_soup_by_url(session: Session, url: str, request_headers: dict = None):
    if request_headers:
        response = session.get(url, headers=request_headers)
    else:
        response = session.get(url)
    response_html = response.content.decode()
    return BeautifulSoup(response_html, 'html.parser')
