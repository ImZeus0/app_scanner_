import time

import requests
from bs4 import BeautifulSoup


class AppParser():

    def __init__(self,package):
        self.package = package

    def _get_link(self):
        return f'https://play.google.com/store/apps/details?id={self.package}&hl=en&gl=US'

    def _request(self,url):
        return requests.get(url)

    def _get_count_install(self,text):
        soup = BeautifulSoup(text,'html.parser')
        element = soup.find_all('div',{'class':'ClM7O'})
        if element[0].text.find('star') != -1:
            return element[1].text
        return element[0].text


    def check(self):
        url = self._get_link()
        res = self._request(url)
        if res.status_code == 200:
            return {'status':0,'count':self._get_count_install(res.text)}
        elif res.status_code == 400:
            return {'status': 1, 'msg':'not found'}
        else:
            print(f'Error open app {self.package} status:{res.status_code} err:{res.text}')

