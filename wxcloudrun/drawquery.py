#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/3/7 4:40 下午
# @Author: zhoumengjie
# @File  : drawquery.py
import os

import requests
import pdfplumber

cninfo_host = 'http://www.cninfo.com.cn'
cninfo_static_host = 'http://static.cninfo.com.cn/'

def query_org_id(stock_code):
    param = {"keyWord": stock_code, 'maxNum': 10}
    r = requests.post(cninfo_host + "/new/information/topSearch/query", params=param)
    if r.status_code != 200:
        print("查询org_id失败：status_code = " + str(r.status_code))
        return None
    return r.json()[0]['orgId']

def query_bond_announcement(stock_code):
    org_id = query_org_id(stock_code)
    if org_id is None:
        return None
    param = {"stock": stock_code + "," + org_id, 'tabName': 'fulltext', 'pageSize': 30, 'pageNum': 1, 'plate': 'bond',
             'category': 'category_kzzq_szsh'}
    r = requests.post(cninfo_host + "/new/hisAnnouncement/query", params=param)
    if r.status_code != 200:
        print("查询转债公告列表失败：status_code = " + str(r.status_code))
        return None
    return r.json()

def query_anno_pdf(file_name, path):
    r = requests.get(cninfo_static_host + path)
    if r.status_code != 200:
        print("下载文件失败：status_code = " + str(r.status_code))
        return None
    with open(file_name, "wb") as code:
        code.write(r.content)
    return file_name

def extract_draw_table(path):
    tables = []
    with pdfplumber.open(path) as pdf:
        pages = pdf.pages
        for page in pages:
            for table in page.extract_tables():
                tables.append(table)
    return tables

def query_draw(stock_code, apply_no):

    data = query_bond_announcement(stock_code)

    anno_list = data['announcements']

    if len(anno_list) == 0:
        print('no anno list...')
        return '还未公布中签结果'

    draw_result = [ele for ele in anno_list if (str(ele['announcementTitle']).find('中签号码公告') != -1 or str(ele['announcementTitle']).find('中签结果公告') != -1)]

    if len(draw_result) == 0:
        print('no announcement...')
        return '还未公布中签结果'

    draw_data = draw_result[0]

    pdf_path = '查询中签结果' + stock_code + '.pdf'
    query_anno_pdf(pdf_path, draw_data['adjunctUrl'])

    table_data = extract_draw_table(pdf_path)

    if table_data is None or len(table_data) == 0:
        print('no draw table data...')
        return '还未公布中签结果'

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
    return '恭喜中签' if len(draw_nos) != 0 else '很遗憾未中签'

def is_lucky_number(apply_no, lucky_rules):
    for rule in lucky_rules:
        is_lucky = str(apply_no).endswith(rule)
        if is_lucky:
            return True
    return False

if __name__ == '__main__':
    is_lucky = query_draw('601838', 109786244938)
    print(is_lucky)