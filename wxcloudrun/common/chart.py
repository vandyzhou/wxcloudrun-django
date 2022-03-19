#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/15 4:14 下午
# @Author: zhoumengjie
# @File  : chart.py
import base64
import random
from datetime import date, timedelta

import tushare as ts
from pyecharts.charts import Kline, Bar
from pyecharts import options as opts
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
from wxcloudrun.bond import PageTemplate as pt
from wxcloudrun.bond.BondUtils import Crawler
from wxcloudrun.common import fingerprinter as fp

from wxcloudrun.share import shareclient

crawler = Crawler()

today = date.today()

class ChartClient:

    def __init__(self, basic=False):
        if not basic:
            self.__token = '0d6ef5ba51b4254c71dd8960ed42ca272410541d8fa45019a45f9f86'
        else:
            flag = random.randint(0, 1000) % 4
            if flag == 0:
                self.__token = 'f8a31b475bf922975f96a35c9b8bdbebc119d9e3026fef88538289d7'
            elif flag == 1:
                self.__token = 'fca41e4c769f7abbd11ba5fb46487dcee02a9c9aff56a60d7a5263f7'
            elif flag == 2:
                self.__token = 'f0ed47f2292e1d157f32d5d033808a6ad96dfd02319120ba475082e6'
            else:
                self.__token = 'd371516f1334bcf9bcb50bed5930b7e226fb69a13e822969df0308c7'
        self.__pro = ts.pro_api(self.__token)

    def get_daily_image(self, stock_code, stock_name, start_date, end_date, add_finger_print=False):
        data = self.__pro.query('daily', ts_code=stock_code, start_date=start_date, end_date=end_date)
        # print(data)
        ochl = data[['open', 'close', 'low', 'high']]
        ochl_tolist = [ochl.iloc[i].tolist() for i in range(len(ochl))]

        kline = Kline(
            init_opts=opts.InitOpts(
                bg_color='#FFFFFF'
            ))\
            .add_xaxis((data['trade_date']).tolist()[::-1])\
            .add_yaxis(series_name='日线图', y_axis=ochl_tolist[::-1], itemstyle_opts=opts.ItemStyleOpts(color="#ff0000", color0="#006600"))\
            .set_global_opts(
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                xaxis_opts=opts.AxisOpts(is_scale=True),
                # datazoom_opts=[opts.DataZoomOpts(type_="inside")], 可缩放
                title_opts=opts.TitleOpts(title=stock_name + "从申购日到至今股价走势"),
            )
        # kline.render('kline.html')
        image_file = stock_name + '_' + stock_code + '.png'
        make_snapshot(snapshot, kline.render(), image_file)

        # 添加水印
        if add_finger_print:
            fp.add_finger_print(image_file)

        with open(image_file, 'rb') as f:
            pic_base64 = base64.b64encode(f.read())

        return ochl_tolist[len(ochl_tolist) - 1][1], ochl_tolist[0][1], pic_base64

    def get_bond_summary(self, add_finger_print=False):

        today_str = date.today().strftime('%Y-%m-%d')

        df = shareclient.get_bond_data()
        avg = df['changepercent'].mean()
        yaxis = []
        for key, val in pt.BOND_DISTRIBUTE_MAP.items():
            if '平' == key:
                count = len(df[df.changepercent==0])
            else:
                count = len(df[(val['high'] > df.changepercent) & (df.changepercent >= val['low'])])
            yaxis.append(opts.BarItem(name=key, value=count, itemstyle_opts=opts.ItemStyleOpts(color=val['color'])))

        bar = Bar(init_opts=opts.InitOpts(bg_color='#FFFFFF'))\
            .add_xaxis(list(pt.BOND_DISTRIBUTE_MAP.keys()))\
            .add_yaxis('涨跌幅度[均值' + str(round(avg, 2)) + '%]', yaxis, category_gap=4) \
            .set_global_opts(title_opts=opts.TitleOpts(title=today_str + "可转债市场涨跌统计"),
                             xaxis_opts=opts.AxisOpts(name='涨跌幅度/%', axislabel_opts={"interval": "0"}),
                             yaxis_opts=opts.AxisOpts(name='可转债数量/只')
                             )

        image_file = '转债_' + today_str + '.png'
        make_snapshot(snapshot, bar.render(), image_file)

        # 加水印
        if add_finger_print:
            fp.add_finger_print(image_file)

        with open(image_file, 'rb') as f:
            pic_base64 = base64.b64encode(f.read())

        return df, pic_base64

    def get_company_info(self, stock_code):
        r"""
        https://tushare.pro/document/2?doc_id=112
        :param stock_code:
        :return:
        """
        list = self.__pro.query('stock_company', ts_code=stock_code, fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province,business_scope,main_business,introduction')
        return list.iloc[0]

    def get_stock_info(self, stock_code, trade_date=None):
        if trade_date is None:
            trade_date = date.today().strftime('%Y%m%d')
        list = self.__pro.query('bak_basic', ts_code=stock_code, trade_date='20220126')
        return list

    def get_today_news(self):
        '''
        https://tushare.pro/document/2?doc_id=195
        :return:
        '''
        tomorrow = today + timedelta(days=1)
        today_str = today.strftime('%Y-%m-%d')
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        data = self.__pro.query('major_news',
                                start_date=today_str + ' 00:00:00',
                                end_date=tomorrow_str + ' 00:00:00',
                                fields='title,content,pub_time,src')
        return data

    def is_trade_open(self, date=None):
        '''
        https://tushare.pro/document/2?doc_id=26
        0休市 1交易
        true是开市
        :return:
        '''
        if date is None:
            date_str = today.strftime('%Y%m%d')
        else:
            date_str = date.strftime('%Y%m%d')
        data = self.__pro.query('trade_cal', start_date=date_str, end_date=date_str)
        return data.iloc[0]['is_open'] == 1

    def next_trade_day(self, date):
        is_open = self.is_trade_open(date)
        if is_open:
            return date
        return self.next_trade_day(date + timedelta(days=1))

    def last_trade_day(self, date):
        is_open = self.is_trade_open(date)
        if is_open:
            return date
        return self.last_trade_day(date + timedelta(days=-1))

    def moneyflow_hsgt(self):
        '''
        https://tushare.pro/document/2?doc_id=47
        :return:
        '''
        date = today.strftime('%Y%m%d')
        data = self.__pro.query('moneyflow_hsgt', start_date=date, end_date=date)
        if data.empty:
            return None
        return data.iloc[0]

    def hsgt_top10(self):
        '''
        https://tushare.pro/document/2?doc_id=48
        :return:
        '''
        date = today.strftime('%Y%m%d')
        data = self.__pro.query('hsgt_top10', trade_date=date)
        if data.empty:
            return None
        return data

    def top10_holders(self, stock_code):
        '''
        https://tushare.pro/document/2?doc_id=61
        :param stock_code:
        :return:
        '''
        suff = crawler.query_stock_suff(stock_code)
        data = self.__pro.query('top10_holders', ts_code=stock_code + '.' + suff.upper())
        return data

    def concept_detail(self, stock_code):
        '''
        https://tushare.pro/document/2?doc_id=126
        :param stock_code:
        :return:
        '''
        suff = crawler.query_stock_suff(stock_code)
        data = self.__pro.query('concept_detail', ts_code=stock_code + '.' + suff.upper())
        return data

    def get_daily_stock(self, stock_code, date):
        suff = crawler.query_stock_suff(stock_code)
        data = self.__pro.query('daily', ts_code=stock_code + '.' + suff.upper(), start_date=date, end_date=date)
        return data


if __name__ == '__main__':
    chart = ChartClient(True)
    # data = chart.concept_detail('002989')
    # names = data['concept_name'].values.tolist()
    # concept_names = data[['concept_name']]
    # ochl_tolist = [concept_names.iloc[i].tolist() for i in range(len(concept_names))]
    # print(ochl_tolist)
    data = chart.get_daily_stock('002989', '20220311')
    print(data)

