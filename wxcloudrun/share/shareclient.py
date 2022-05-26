#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/25 12:12 下午
# @Author: zhoumengjie
# @File  : shareclient.py
import json
import re
import time

import lxml
import lxml.html
from lxml import etree
from io import StringIO

from pandas import DataFrame
from pandas import json_normalize

from wxcloudrun.share import cons as ct
from urllib.request import Request, urlopen

import pandas as pd

def get_bond_data() -> DataFrame:
    r"""
    获取沪深可转债的交易数据
    :return:
    """
    ct._write_head()
    df = _get_bond_data(1, pd.DataFrame())
    if df is not None:
        ds = df[(df['volume'] != 0)]
        ds = ds.reset_index(drop=True)
        ds['changepercent'] = ds['changepercent'].map(lambda x: float(x))
        ds['amount'] = ds['amount'].map(lambda x: int(x))
        ds['high'] = ds['high'].map(lambda x: float(x))
        ds['low'] = ds['low'].map(lambda x: float(x))
        ds['open'] = ds['open'].map(lambda x: float(x))
        ds['amplitude'] = ds.apply(lambda x: (x['high'] - x['low'])/x['open'], axis=1)
    return ds

def _get_bond_data(pageNo, dataArr, retry_count=3, pause=0.001):
    ct._write_console()
    for _ in range(retry_count):
        time.sleep(pause)
        try:
            request = Request(ct.BOND_URL % (ct.P_TYPE['http'], ct.DOMAINS['vsf'], pageNo, ct.PAGE_NUM[1]))
            text = urlopen(request, timeout=10).read()
            text = text.decode('GBK')
            json_data = json.loads(text)
            df = json_normalize(json_data)
            if len(df) == 0:
                return dataArr
            df.columns = ct.BOND_COLS
            dataArr = dataArr.append(df, ignore_index=True)
            if len(json_data) == ct.PAGE_NUM[1]:
                pageNo += 1
                return _get_bond_data(pageNo, dataArr)
            else:
                return dataArr
        except Exception as e:
            pass
    raise IOError(ct.NETWORK_URL_ERROR_MSG)


def get_report_data(year, quarter):
    """
        获取业绩报表数据
    Parameters
    --------
    year:int 年度 e.g:2014
    quarter:int 季度 :1、2、3、4，只能输入这4个季度
       说明：由于是从网站获取的数据，需要一页页抓取，速度取决于您当前网络速度

    Return
    --------
    DataFrame
        code,代码
        name,名称
        eps,每股收益
        eps_yoy,每股收益同比(%)
        bvps,每股净资产
        roe,净资产收益率(%)
        epcf,每股现金流量(元)
        net_profits,净利润(万元)
        profits_yoy,净利润同比(%)
        distrib,分配方案
        report_date,发布日期
    """
    if ct._check_input(year, quarter) is True:
        ct._write_head()
        df = _get_report_data(year, quarter, 1, pd.DataFrame())
        if df is not None:
            df['code'] = df['code'].map(lambda x: str(x).zfill(6))
        return df


def _get_report_data(year, quarter, pageNo, dataArr,
                     retry_count=3, pause=0.001):

    r"""
    xpath使用语法：https://www.cnblogs.com/zhangxinqi/p/9210211.html
    :param year:
    :param quarter:
    :param pageNo:
    :param dataArr:
    :param retry_count:
    :param pause:
    :return:
    """

    ct._write_console()
    for _ in range(retry_count):
        time.sleep(pause)
        try:
            request = Request(ct.REPORT_URL % (ct.P_TYPE['http'], ct.DOMAINS['vsf'], ct.PAGES['fd'],
                                               year, quarter, pageNo, ct.PAGE_NUM[1]))
            text = urlopen(request, timeout=10).read()
            text = text.decode('GBK')
            text = text.replace('--', '')
            html = lxml.html.parse(StringIO(text))
            res = html.xpath("//table[@class=\"list_table\"]/tr")
            if ct.PY3:
                sarr = [etree.tostring(node).decode('utf-8') for node in res]
            else:
                sarr = [etree.tostring(node) for node in res]
            sarr = ''.join(sarr)
            sarr = '<table>%s</table>' % sarr
            df = pd.read_html(sarr)[0]
            df = df.drop(11, axis=1)
            df.columns = ct.REPORT_COLS
            dataArr = dataArr.append(df, ignore_index=True)
            nextPage = html.xpath('//div[@class=\"pages\"]/a[last()]/@onclick')
            if len(nextPage) > 0:
                pageNo = re.findall(r'\d+', nextPage[0])[0]
                return _get_report_data(year, quarter, pageNo, dataArr)
            else:
                return dataArr
        except Exception as e:
            pass
    raise IOError(ct.NETWORK_URL_ERROR_MSG)

if __name__ == '__main__':
    df = get_bond_data()
    sum_amount = df['amount'].sum()
    up_count = len(df[df.changepercent > 0])
    down_count = len(df[df.changepercent < 0])
    change_sort_df = df.sort_values(by=['changepercent'], ascending=[False])
    high = change_sort_df.head(1)
    low = change_sort_df.tail(1)
    amplitude_sort_df = df.sort_values(by=['amplitude'], ascending=[False])
    print(amplitude_sort_df.head(3))