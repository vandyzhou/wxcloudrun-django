#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/29 10:35 上午
# @Author: zhoumengjie
# @File  : pdfutils.py
import base64
import math
import time

import pdfplumber
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
from selenium import webdriver

from wxcloudrun.bond.BondUtils import Crawler
from wxcloudrun.bond.PageTemplate import PROJECT_DIR
from wxcloudrun.common import fingerprinter as fp
from wxcloudrun.common import tabledrawer

crawler = Crawler()

def extract_draw_table(path):
    tables = []
    with pdfplumber.open(path) as pdf:
        pages = pdf.pages
        for page in pages:
            for table in page.extract_tables():
                tables.append(table)
    return tables

def get_draw_pdf_table(url_path, bond_name, add_finger_print=False):
    file_name = bond_name + '_anno' + '.pdf'
    crawler.query_anno_pdf(file_name, url_path)
    img_file = bond_name + '_draw' + '.png'
    return draw_table(file_name, img_file, bond_name, add_finger_print)

def draw_table(pdf_path, img_file, bond_name, add_finger_print=False):
    table_data = extract_draw_table(pdf_path)
    if table_data is None or len(table_data) == 0:
        print('未识别到pdf的中签表格')
        return None

    if bond_name == '聚合转债':
        headers = table_data[2][0]
        rows = table_data[2][1:]

    if len(table_data) == 1:
        headers = table_data[0][0]
        rows = table_data[0][1:]
    if len(table_data) == 2:
        headers = table_data[0][0]
        # 表头相同
        if headers == table_data[1][0]:
            rows = table_data[0][1:] + table_data[1][1:]
        else:
            rows = table_data[0][1:] + table_data[1][0:]

    # 过滤空行
    rows = filter(lambda row : is_valid_row(row), rows)
    # tabledrawer.draw_table(headers, rows)
    table = Table()
    table.add(headers, rows)
    table.set_global_opts(title_opts=ComponentTitleOpts(title="配售结果"))

    render_file_name = bond_name + "_table-screenshot.html"
    table.render(render_file_name)

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(chrome_options=options)
    driver.get("file://" + PROJECT_DIR + '/' + render_file_name)
    time.sleep(1)
    ele = driver.find_element_by_xpath("//tbody")
    ele.screenshot(img_file)

    # 添加水印
    if add_finger_print:
        fp.add_finger_print(img_file)

    with open(img_file, 'rb') as f:
        pic_base64 = base64.b64encode(f.read())

    return pic_base64, table_data

def is_valid_row(row:[]):
    if len(row) == 0:
        return False
    count = len(row)
    for cell in row:
        if cell is None or cell=='':
            count -= 1
    return count != 0

if __name__ == '__main__':
    # get_draw_pdf_table('/finalpage/2022-01-26/1212274930.PDF', '豪美转债')
    # draw_table(PROJECT_DIR + '/中特转债_anno.pdf', '2.png', '中特转债')
    # table = extract_draw_table(PROJECT_DIR + '/中特转债_anno.pdf')
    # print(table)
    print(math.ceil(1 / float(0.14)))