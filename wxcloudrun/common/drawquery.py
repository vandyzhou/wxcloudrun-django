#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/3/7 4:40 下午
# @Author: zhoumengjie
# @File  : drawquery.py
import datetime
import os

from wxcloudrun.bond.jisilu import crawler
from wxcloudrun.common import pdfutils


def query_draw(stock_code, apply_no):

    data = crawler.query_bond_announcement(stock_code)

    anno_list = data['announcements']

    if len(anno_list) == 0:
        print('no anno list...')
        return False

    draw_result = [ele for ele in anno_list if (str(ele['announcementTitle']).find('中签号码公告') != -1 or str(ele['announcementTitle']).find('中签结果公告') != -1)]

    if len(draw_result) == 0:
        print('no announcement...')
        return False

    draw_data = draw_result[0]

    pdf_path = '查询中签结果' + stock_code + '.pdf'
    crawler.query_anno_pdf(pdf_path, draw_data['adjunctUrl'])

    table_data = pdfutils.extract_draw_table(pdf_path)

    if table_data is None or len(table_data) == 0:
        print('no draw table data...')
        return False

    if len(table_data) == 1:
        rows = table_data[0][1:]

    if len(table_data) == 2:
        headers = table_data[0][0]
        # 表头相同
        if headers == table_data[1][0]:
            rows = table_data[0][1:] + table_data[1][1:]
        else:
            rows = table_data[0][1:] + table_data[1][0:]

    lucky_rules = []

    for row in rows:
        for i in range(1, len(row)):
            lucky_nos = row[i].replace('\n', '').replace(' ', '').split('，')
            lucky_rules += lucky_nos

    draw_nos = []

    for i in range(apply_no, apply_no + 1000):
        if is_lucky_number(i, lucky_rules):
            draw_nos.append(i)

    print(draw_nos)
    # 删除文件
    os.remove(pdf_path)
    return len(draw_nos) != 0

def is_lucky_number(apply_no, lucky_rules):
    for rule in lucky_rules:
        is_lucky = str(apply_no).endswith(rule)
        if is_lucky:
            return True
    return False

if __name__ == '__main__':
    is_lucky = query_draw('601838', 109786244938)
    print(is_lucky)