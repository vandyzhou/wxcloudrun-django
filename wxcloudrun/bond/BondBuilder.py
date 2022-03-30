#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/8 8:01 下午
# @Author: zhoumengjie
# @File  : BondBuilder.py

class BondPage:

    def __init__(self):
        # 申购评测
        self.apply_bonds = []
        # 证监会核准/同意注册
        self.next_bonds = []
        # 已申购完，即将上市的
        self.ipo_bonds = []
        # 隔日上市
        self.prepare_bonds = []
        # 即将申购
        self.applying_bonds = []
        # 今天上市的
        self.today_bonds = []
        # 中签结果
        self.draw_bonds = []
        # 发审委通过
        self.pass_bonds = []

class CompanyInfo:
    def __init__(self, data):
        #公司名称
        self.gsmc = data['jbzl']['gsmc']
        #英文名称
        self.ywmc = data['jbzl']['ywmc']
        #曾用名
        self.cym = data['jbzl']['cym']
        #A股代码
        self.agdm = data['jbzl']['agdm']
        #A股简称
        self.agjc = data['jbzl']['agjc']
        #B股代码
        self.bgdm = data['jbzl']['bgdm']
        #B股简称
        self.bgjc = data['jbzl']['bgjc']
        #H股代码
        self.hgdm = data['jbzl']['hgdm']
        #H股简称
        self.hgjc = data['jbzl']['hgjc']
        #所属市场
        self.ssjys = data['jbzl']['ssjys']
        #所属行业
        self.sszjhhy = data['jbzl']['sszjhhy']
        #法人代表
        self.frdb = data['jbzl']['frdb']
        #注册资金
        self.zczb = data['jbzl']['zczb']
        #成立日期
        self.clrq = data['fxxg']['clrq']
        #上市日期
        self.ssrq = data['fxxg']['ssrq']
        #注册地址
        self.zcdz = data['jbzl']['zcdz']
        #经营范围
        self.jyfw = data['jbzl']['jyfw']
        #公司简介
        self.gsjj = data['jbzl']['gsjj']


class BondInfo:
    def __init__(self, row):
        self.stock_code = row.get('stock_id', '-')
        self.bond_code = row.get('bond_id', '-')
        self.bond_name = row.get('bond_nm', '-')
        self.stock_name = row.get('stock_nm', '-')
        # 总金额 数字
        self.amount = row.get('amount', '-')
        # 评级
        self.grade = row.get('rating_cd', '-')
        # 正股价 数字
        self.price = row.get('price', '-')
        # 转股价 数字
        self.convert_price = row.get('convert_price', '-')
        # 股东配售率 字符串 62.100
        self.ration_rt = row.get('ration_rt', '-')
        # 正股现价比转股价 字符串 97.11
        self.pma_rt = row.get('pma_rt', '-')
        # 正股pb 数字
        self.pb = row.get('pb', '-')
        # 百元股票含权 数字
        self.cb_amount = row.get('cb_amount', '-')
        # 每股配售（元） 数字
        self.ration = row.get('ration', '-')
        # 配送10张所需股数 数字
        self.apply10 = row.get('apply10', '-')
        # 股权登记日 字符
        self.record_dt = row.get('record_dt', '-')
        # 网上规模 字符
        self.online_amount = row.get('online_amount', '-')
        # 中签率 字符 "0.0238"
        self.lucky_draw_rt = row.get('lucky_draw_rt', '-')
        # 单帐户中签（顶格） 字符 0.2377
        self.single_draw = row.get('single_draw', '-')
        # 申购户数 数字
        self.valid_apply = row.get('valid_apply', '-')
        # 申购日期 字符
        self.apply_date = row.get('apply_date', '-')
        # 方案进展 字符 发行流程：董事会预案 → 股东大会批准 → 证监会受理 → 发审委通过 → 证监会核准/同意注册 → 发行公告
        self.progress_nm = row.get('progress_nm', '-')
        # 进展日期 yyyy-MM-dd
        self.progress_dt = row.get('progress_dt', '-')
        # 上市日期
        self.list_date = row.get('list_date', '-')
        # 申购标志：E:已申购待上市已排期、D:已上市、B:待申购、C:已申购未有上市排期、N:证监会核准/同意注册
        self.ap_flag = row.get('ap_flag', '-')

class BondData:
    def __init__(self, row):
        self.stock_code = row.get('stock_id', '-')
        self.bond_code = row.get('bond_id', '-')
        self.bond_name = row.get('bond_nm', '-')
        self.stock_name = row.get('stock_nm', '-')
        # 涨跌幅 数字 -1.98
        self.increase_rt = row.get('increase_rt', '-')
        # 正股价 数字
        self.sprice = row.get('sprice', '-')
        # 现价 数字
        self.price = row.get('price', '-')
        # 正股涨跌 数字 -3.03
        self.sincrease_rt = row.get('sincrease_rt', '-')
        # 正股pb 数字
        self.pb = row.get('pb', '-')
        # 转股价 数字
        self.convert_price = row.get('convert_price', '-')
        # 转股价值 数字
        self.convert_value = row.get('convert_value', '-')
        # 溢价率 数字 18.41
        self.premium_rt = row.get('premium_rt', '-')
        # 评级
        self.grade = row.get('rating_cd', '-')
        # 回售触发价 数字
        self.put_convert_price = row.get('put_convert_price', '-')
        # 强赎触发价 数字
        self.force_redeem_price = row.get('force_redeem_price', '-')
        # 转债占比
        self.convert_amt_ratio = row.get('convert_amt_ratio', '-')
        # 到期时间
        self.short_maturity_dt = row.get('short_maturity_dt', '-')
        # 剩余年限 数字
        self.year_left = row.get('year_left', '-')
        # 剩余规模 数字
        self.curr_iss_amt = row.get('curr_iss_amt', '-')
        # 剩余年限 数字
        self.year_left = row.get('year_left', '-')
        # 成交额 数字
        self.volume = row.get('volume', '-')
        # 换手率 数字
        self.turnover_rt = row.get('turnover_rt', '-')
        # 到期税前收益 数字
        self.ytm_rt = row.get('ytm_rt', '-')
        # 双低 数字
        self.dblow = row.get('dblow', '-')

class ForceBondInfo:
    def __init__(self, row):
        self.stock_code = row.get('stock_id', '-')
        self.bond_code = row.get('bond_id', '-')
        self.bond_name = row.get('bond_nm', '-')
        self.stock_name = row.get('stock_nm', '-')
        # 债券价 字符 "355.000"
        self.price = row.get('price', '-')
        # 最后交易日 字符
        self.redeem_dt = row.get('redeem_dt', '-')
        # 简介 字符 "最后交易日：2022年1月27日\r\n最后转股日：2022年1月27日\r\n赎回价：100.21元/张"
        self.force_redeem = row.get('force_redeem', '-')
        # 转股起始日 字符
        self.convert_dt = row.get('convert_dt', '-')
        # 剩余规模 字符 "355.00"
        self.curr_iss_amt = row.get('curr_iss_amt', '-')
        # 强赎触发价 字符 "355.00"
        self.force_redeem_price = row.get('force_redeem_price', '-')
        # 规模 字符 "355.000"
        self.orig_iss_amt = row.get('orig_iss_amt', '-')
        # 强赎价 字符 "355.000"
        self.real_force_redeem_price = row.get('real_force_redeem_price', '-')
        # 强赎标志 字符 "Y" N
        self.redeem_flag = row.get('redeem_flag', '-')
        # 没懂~~ 字符 "355.00"
        self.redeem_price = row.get('redeem_price', '-')
        # 强赎触发比 字符 "355%"
        self.redeem_price_ratio = row.get('redeem_price_ratio', '-')
        # 强赎条款 字符
        self.redeem_tc = row.get('redeem_tc', '-')
        # 正股价 字符 "34.45"
        self.sprice = row.get('sprice', '-')
        # 剩余天数 数字
        self.redeem_count_days = row.get('redeem_count_days', '-')
        # 总天数 数字
        self.redeem_real_days = row.get('redeem_real_days', '-')
        # R=已要强赎、O=公告要强赎、G=公告不强赎
        self.redeem_icon = row.get('redeem_icon', '-')