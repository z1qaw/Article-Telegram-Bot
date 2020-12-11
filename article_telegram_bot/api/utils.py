from bs4 import BeautifulSoup
from requests import Session


def get_html_soup_by_url(session: Session, url: str, request_headers: dict = None, verify=True):
    if request_headers:
        response = session.get(url, headers=request_headers, verify=verify)
    else:
        response = session.get(url, verify=verify)
    response_html = response.content.decode()
    return BeautifulSoup(response_html, 'html.parser')
