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

    def _format_to_int(self,num_str):
        num = num_str.replace('+', '')
        if 'K' in num:
            num = num.replace('K', '')
            num = int(num) * 1000
        elif 'M' in num:
            num = num.replace('M', '')
            num = int(num) * 1000000
        elif 'B' in num:
            num = num.replace('B', '')
            num = int(num) * 1000000000
        else:
            num = int(num)
        return num
    def _get_count_install(self,text):
        soup = BeautifulSoup(text,'html.parser')
        element = soup.find_all('div',{'class':'ClM7O'})
        if element[0].text.find('star') != -1:
            return self._format_to_int(element[1].text)
        return self._format_to_int(element[0].text)



    def check(self):
        url = self._get_link()
        res = self._request(url)
        if res.status_code == 200:
            return {'status':0,'count':self._get_count_install(res.text)}
        elif res.status_code == 400:
            return {'status': 1, 'msg':'not found'}
        else:
            print(f'Error open app {self.package} status:{res.status_code} err:{res.text}')

