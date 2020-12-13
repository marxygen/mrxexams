import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

URL = 'https://dictionary.cambridge.org/ru/словарь/англо-русский/%s'
requests.packages.urllib3.disable_warnings()

def parse(word):
    ua = UserAgent()
    header = {'User-Agent':str(ua.random)}
    response = requests.get(URL%word, headers=header, verify=False)
    translation = ''
    link = URL%word

    try:
        soup = BeautifulSoup(response.text, features='lxml')
        translation = soup.find('span', {'class': 'trans dtrans dtrans-se '}).text.strip()
    finally:
        return translation
