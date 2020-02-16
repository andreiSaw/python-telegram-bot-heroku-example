from bs4 import BeautifulSoup
import requests
import os

_HEADERS = {
    'Referer': 'https://www.abc.com/',
    'User-Agent': 'Mozilla/5.0'
}
_MODE = os.getenv("MODE")
_TOKEN = os.getenv("TOKEN")
_REQUEST_KWARGS = {
    'proxy_url': 'socks5://176.9.144.68:1080',
    'urllib3_proxy_kwargs': {
        'username': os.getenv('PROXY_USER'),
        'password': os.getenv('PROXY_PASS'),
    }
}


def get_data(the_link: str):
    s = requests.Session()
    s.headers.update(_HEADERS)
    request = s.get(the_link)
    soup = BeautifulSoup(request.text, features="html.parser")
    return soup.find('div', {'class': "main-horoscope"}).findAll('p')[0].text
