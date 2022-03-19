#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/16 9:04 下午
# @Author: zhoumengjie
# @File  : ScreenShotUtil.py
import base64

import requests
from bs4 import BeautifulSoup
from html2image import Html2Image


def nba_summary_save(mid:str, file_name):
    r""" 保存图片
    :return:
    """
    snapshot = SnapShot('https://slamdunk.sports.sina.com.cn', '/match/stats', param={'mid': mid})
    html_str = snapshot.get_dom('div', 'part01')
    print(html_str)
    # with open('framework.css', 'r') as f:
    #     css_str = f.read()
    snapshot.hti.screenshot(html_str=html_str, save_as=file_name)
    with open(file_name, 'rb') as f:
        pic_base64 = base64.b64encode(f.read())
    return pic_base64

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
    text = nba_summary_save('9426c38e-48d6-4441-8607-9e9f4d311bab', 'xx.png')
    print(text)