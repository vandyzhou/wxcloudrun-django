#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/3/15 5:15 下午
# @Author: zhoumengjie
# @File  : akclient.py
import logging
from datetime import date, timedelta

import akshare as ak
import numpy as np
from pandas import DataFrame
from texttable import Texttable

# document https://akshare.xyz/data/stock/stock.html

log = logging.getLogger('log')

def print_dataframe(df:DataFrame):
    tb = Texttable()
    # tb.set_deco(Texttable.HEADER)
    # tb.set_cols_dtype(['t'] * len(df.columns.tolist()))
    tb.set_cols_align(["r"] * len(df.columns.tolist()))
    # tb.set_cols_align(['l', 'r', 'r'])
    # tb.set_cols_dtype(['t', 'i', 'i'])
    tb.set_cols_width([20] * len(df.columns.tolist()))
    tb.header(df.columns.tolist())
    pre_50 = df.values[0:50]
    pre_50 = np.insert(pre_50, 0, df.columns.tolist(), axis=0)
    tb.add_rows(pre_50)
    log.info(tb.draw())

def stock_zh_index_spot():
    r"""
    返回各个指数涨跌等信息
    :return:
    """
    return ak.stock_zh_index_spot()

def analyst_rank(tag:str='0年收益率'):
    r"""
    根据收益率高的分析师的最新跟踪的股票
    :return:
    """
    df = ak.stock_em_analyst_rank(year='0')
    # 0年收益率、3个月收益率、6个月收益率、12个月收益率
    ds = df.sort_values(by=[tag], ascending=[False])
    rank_10 = ds.head(10)
    for index, row in rank_10.iterrows():
        analyst_id = row['分析师ID']
        detail = ak.stock_em_analyst_detail(analyst_id=analyst_id)
        log.info("{}{}:{}".format(row['分析师名称'], tag, row[tag]))
        log.info(detail)

def stock_hsgt_hold_stock_em(market='北向', indicator='今日排行'):
    r"""
    北向增持个股排行
    :param market:
    :param indicator:
    :return:
    """
    df = ak.stock_hsgt_hold_stock_em(market=market, indicator=indicator)
    return df

def stock_hsgt_hist_em(symbol="沪股通"):
    r"""
    东方财富网-数据中心-资金流向-沪深港通资金流向-沪深港通历史数据
    :param symbol:
    :return:
    """
    df = ak.stock_hsgt_hist_em(symbol=symbol)
    return df

def stock_fund_flow_concept(symbol='即时'):
    r"""
    概念资金流
    :return:
    """
    df = ak.stock_fund_flow_concept(symbol=symbol)
    return df

def stock_fund_flow_industry(symbol='即时'):
    r"""
    行业资金流
    :param symbol:
    :return:
    """
    df = ak.stock_fund_flow_industry(symbol=symbol)
    return df

def stock_zh_a_gdhs_detail_em(symbol):
    r"""
    查询股东户数
    :param symbol:
    :return:
    """
    df = ak.stock_zh_a_gdhs_detail_em(symbol)
    return df

def stock_fund_stock_holder(stock):
    r"""
    基金持股
    :param stock:
    :return:
    """
    df = ak.stock_fund_stock_holder(stock)
    return df

def stock_rank_lxsz_ths():
    r"""
    连续上涨
    :return:
    """
    return ak.stock_rank_lxsz_ths()

def stock_rank_lxxd_ths():
    r"""
    连续下跌
    :return:
    """
    return ak.stock_rank_lxxd_ths()

def stock_rank_cxfl_ths():
    r"""
    持续放量
    :return:
    """
    return ak.stock_rank_cxfl_ths()

def stock_rank_cxsl_ths():
    r"""
    持续缩量
    :return:
    """
    return ak.stock_rank_cxsl_ths()

def stock_rank_ljqs_ths():
    r"""
    量价齐升
    :return:
    """
    return ak.stock_rank_ljqs_ths()

def stock_rank_ljqd_ths():
    r"""
    量价齐跌
    :return:
    """
    return ak.stock_rank_ljqd_ths()

def stock_cg_equity_mortgage_cninfo(choose_date=None):
    r"""
    查询质押信息
    :param choose_date:
    :return:
    """
    if choose_date is None:
        choose_date = (date.today() + timedelta(days=-1))
    try:
        df = ak.stock_cg_equity_mortgage_cninfo(date=choose_date.strftime('%Y%m%d'))
        return df
    except:
        choose_date = (choose_date + timedelta(days=-1))
        return stock_cg_equity_mortgage_cninfo(choose_date)

def query_stock_summary():
    df = ak.fund_em_exchange_rank()
    dblow_df = df.sort_values(by=['近1周'], ascending=[False])
    print(len(dblow_df))
    return dblow_df

if __name__ == '__main__':
    data = query_stock_summary()
    print_dataframe(data)