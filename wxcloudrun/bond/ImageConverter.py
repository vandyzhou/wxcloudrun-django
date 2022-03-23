#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/8 4:39 下午
# @Author: zhoumengjie
# @File  : ImageConverter.py
import base64
import os

import requests
from bs4 import BeautifulSoup, element
from html2image import Html2Image
import re
from PIL import Image
from wxcloudrun.common import fingerprinter as fp

from wxcloudrun.bond.PageTemplate import PROJECT_DIR

jisilu_host = 'https://www.jisilu.cn'

class ImageConverter:

    def __init__(self, code, code_name='', domain=jisilu_host, path='/data/convert_bond_detail/'):
        self.__hti = Html2Image(custom_flags=[
            '--default-background-color=0',
            '--hide-scrollbars',
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ])
        self.__code = code
        self.__code_name = code_name
        self.__url = domain + path + code

    def get_dom(self, node='div', class_='info_data'):
        r""" 获取dom
        :return:
        """
        r = requests.get(self.__url)
        soup = BeautifulSoup(r.text, 'html.parser', from_encoding='utf-8')
        target = soup.find(node, class_=class_)

        #处理一下表格
        rows = target.find_all('table')[0]('tr')
        purpose = ''
        before_benefit = ''
        after_benefit = ''
        down_rate = '无'
        redeem_rate = '无'
        resale_rate = '无'
        if len(rows) > 0:
            for row in rows:
                if str(row.text).find('我的备注') != -1:
                    # 删除这个节点
                    row.extract()
                    continue
                if str(row.text).find('税前收益') != -1:
                    before_benefit = str(row('td')[2].text).replace('税前收益：', '')
                    continue
                if str(row.text).find('税后收益') != -1:
                    after_benefit = str(row('td')[2].text).replace('税后收益：', '')
                    continue
                if str(row.text).find('共享计划') != -1:
                    [content.extract() for content in row.contents]
                    # 注释
                    if type(row.nextSibling) == element.Comment:
                        row.nextSibling.extract()
                    continue
                if str(row.text).find('转股价下修') != -1:
                    # 不能continue，因为购买会员在这行
                    nums = re.findall(r"\d+%", row('td')[1].text)
                    if len(nums) > 0:
                        down_rate = nums[0]
                if str(row.text).find('购买会员') != -1:
                    contents = row('td')[1].contents
                    del contents[1:len(contents)]
                    continue
                if str(row.text).find('募资用途') != -1:
                    purpose = row('td')[1].text
                    continue
                if str(row.text).find('强制赎回') != -1:
                    nums = re.findall(r"\d+%", row('td')[1].text)
                    if len(nums) > 0:
                        redeem_rate = nums[0]
                    continue
                if str(row.text).find('回售') != -1:
                    nums = re.findall(r"\d+%", row('td')[1].text)
                    if len(nums) > 0:
                        resale_rate = nums[0]
                    continue

        links = target.find_all('a')
        industry_code = ''
        industry_text = ''
        if len(links) > 0:
            for link in links:
                if str(link['href']).find('industry') == -1:
                    continue
                p = re.compile('\d+')
                digs = p.findall(str(link['href']))
                industry_code = digs[0]
                industry_text = link.text
                break
        return target.prettify(), industry_code, industry_text, purpose, before_benefit, after_benefit, down_rate, redeem_rate, resale_rate

    def save(self, add_finger_print=False, node='div', class_='info_data'):
        r""" 保存图片
        :return:
        """
        doms = self.get_dom(node, class_)
        html_str = doms[0]
        file_name = self.__code_name + "_" + self.__code + ".png"
        with open(PROJECT_DIR + '/wxcloudrun/common/framework.css', 'r') as f:
            css_str = f.read()
        self.__hti.screenshot(html_str=html_str, css_str=css_str, save_as=file_name, size=[1080, 720])

        # 添加水印
        if add_finger_print:
            fp.add_finger_print(file_name)

        with open(file_name, 'rb') as f:
            pic_base64 = base64.b64encode(f.read())

        # 删除文件
        os.remove(file_name)

        return pic_base64, doms[1], doms[2], doms[3], doms[4], doms[5], doms[6], doms[7], doms[8]

    def resize(self):
        img = Image.open('../img/牛市-1.jpg')
        width = int(img.size[0] * 1)
        height = int(img.size[1] * 1)
        type = img.format
        print(width)
        print(height)
        print(type)
        # out = img.resize((width, height), Image.ANTIALIAS)
        # out.save('bond_127052_high.png', type)



if __name__ == '__main__':
    img = ImageConverter('127052')
    data = img.get_dom()

