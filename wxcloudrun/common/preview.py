#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/15 9:40 下午
# @Author: zhoumengjie
# @File  : preview.py
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def preview(url:str):
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    time.sleep(2)
    # element = driver.find_element_by_tag_name('body')
    # print(element.text)
    # element.send_keys(Keys.CONTROL + 'a')
    # element.send_keys(Keys.CONTROL + 'c')
    # time.sleep(1)
    driver.quit()

if __name__ == '__main__':
    preview('file:///Users/vandyzhou/PycharmProjects/master/110084_decorate.html')
