#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/16 9:04 下午
# @Author: zhoumengjie
# @File  : ScreenShotUtil.py
import base64

import requests
from bs4 import BeautifulSoup
from html2image import Html2Image


class SnapShot:
    def __init__(self, domain, path, param):
        self.hti = Html2Image()
        self.url = domain + path
        self.param = param

    def get_dom(self, node, class_):
        r""" 获取dom
        :return:
        """
        r = requests.get(self.url, params=self.param)
        soup = BeautifulSoup(r.text, 'html.parser', from_encoding='utf-8')
        target = soup.find(node, class_=class_)

        return target.prettify()

if __name__ == '__main__':
    print('')