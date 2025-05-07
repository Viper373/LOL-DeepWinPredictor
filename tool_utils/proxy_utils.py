# -*- coding:utf-8 -*-
# @Project        :XOVideos
# @FileName       :proxy_utils.py
# @Time           :2025/2/4 00:05
# @Software       :PyCharm
# @Author         :Viper373
# @Index          :https://viper3.top
# @Blog           :https://blog.viper3.top

import requests


class ProxyUtils:
    def __init__(self):
        pass

    @staticmethod
    def get_proxy():
        proxies = {}
        proxy_host = '127.0.0.1'
        proxy_port = 7890
        proxies['http'] = f'http://{proxy_host}:{proxy_port}'
        proxies['https'] = f'http://{proxy_host}:{proxy_port}'
        return None
