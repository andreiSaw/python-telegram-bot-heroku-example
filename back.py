from bs4 import BeautifulSoup
import requests

_HEADERS = {
    'Referer': 'https://www.abc.com/',
    'User-Agent': 'Mozilla/5.0'
}


def get_data(the_link: str):
    s = requests.Session()
    s.headers.update(_HEADERS)
    request = s.get(the_link)
    soup = BeautifulSoup(request.text,features="html.parser")
    return soup.find('div', {'class': "main-horoscope"}).findAll('p')[0].text
