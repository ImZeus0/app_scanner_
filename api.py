import requests
from config import BASE_URL_SERVICE


class ServiceApi:

    @classmethod
    def save_scan(cls,data):
        url = BASE_URL_SERVICE + '/history_apps/'
        return requests.post(url, json=data)
    @classmethod
    def update_app_info(cls, id_recored, data):
        url = BASE_URL_SERVICE + '/apps/'
        return requests.put(url,params={'id':id_recored},json=data)
    @classmethod
    def get_app_by_package(cls,package):
        url = BASE_URL_SERVICE + '/apps/by_package'
        return requests.get(url, params={'package': package})

    @classmethod
    def get_blocked(cls, app_id):
        url = BASE_URL_SERVICE + '/apps/blocked'
        return requests.get(url, params={'app_id': app_id})


