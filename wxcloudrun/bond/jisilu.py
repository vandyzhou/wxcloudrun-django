#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/7 4:33 下午
# @Author: zhoumengjie
# @File  : jisilu.py
import base64
import logging
import math
import os
import shutil
import time
from datetime import date, datetime, timedelta
from functools import cmp_to_key

from wxcloudrun.bond.BondBuilder import BondInfo, BondData, ForceBondInfo
from wxcloudrun.bond.BondBuilder import BondPage
from wxcloudrun.bond.BondBuilder import CompanyInfo
from wxcloudrun.bond.BondUtils import Crawler, format_func
from wxcloudrun.bond import PageTemplate as pt
from wxcloudrun.bond.ImageConverter import ImageConverter
import numpy as np

from wxcloudrun.bond.PageTemplate import PROJECT_DIR
from wxcloudrun.common import mdmaker, preview, pdfutils, shellclient, fingerprinter, akclient
from wxcloudrun.common.chart import ChartClient
# from db.dbclient import SqliteClient
# from db.dbmodels import BondMarketSummaryModel, ApplyBondInfoModel, StockMarketSummaryModel
log = logging.getLogger('log')

crawler = Crawler()
# sqlclient = SqliteClient()

tushare = ChartClient()

briefs = []

filter_concept_names = ['同花顺漂亮100', '转融券标的', '融资融券', '融资标的股',
                        '融券标的股', '标普道琼斯A股', '长三角一体化', '年报预增',
                        '沪股通', '深股通', '机构重仓', '北京国资改革', '创业板重组松绑',
                        '核准制次新股', '新股与次新股', '股权转让', '兜底增持', '科创次新股']

# trade_open = tushare.is_trade_open()

def build_bond():

    rows = crawler.query_apply_list()

    if not rows or len(rows) == 0:
        return None

    bond_page = BondPage()
    apply_bonds = []
    next_bonds = []
    ipo_bonds = []
    prepare_bonds = []
    applying_bonds = []
    today_bonds = []
    draw_bonds = []

    today = date.today()
    tomorrow = (today + timedelta(days=1))
    yesterday = (today + timedelta(days=-1))
    next_trade_open_day = tushare.next_trade_day(tomorrow)
    last_trade_open_day = tushare.last_trade_day(yesterday)

    next_open_date = next_trade_open_day.strftime('%Y-%m-%d')
    last_open_date = last_trade_open_day.strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')

    for row in rows:
        if row['cb_type'] != '可转债':
            continue
        if row['apply_date'] == last_open_date:
            draw_bonds.append(BondInfo(row))
        if row['ap_flag'] == 'D' and row['list_date'] == today_str:
            today_bond = BondInfo(row)
            today_bonds.append(today_bond)
            # 不需要continue
        if row['ap_flag'] == 'B' and row['apply_date'] == next_open_date:
            apply_bond = BondInfo(row)
            apply_bonds.append(apply_bond)
            continue
        if row['ap_flag'] == 'E' and row['list_date'] == next_open_date:
            prepare_bond = BondInfo(row)
            prepare_bonds.append(prepare_bond)
            continue
        if row['ap_flag'] == 'B':
            applying_bond = BondInfo(row)
            applying_bonds.append(applying_bond)
            continue
        if row['ap_flag'] == 'N' and row['progress_nm'] == '证监会核准/同意注册':
            next_bond = BondInfo(row)
            next_bonds.append(next_bond)
            continue
        if row['ap_flag'] == 'C' or row['ap_flag'] == 'E':
            ipo_bond = BondInfo(row)
            ipo_bonds.append(ipo_bond)
            continue
    bond_page.apply_bonds = apply_bonds
    bond_page.next_bonds = next_bonds
    bond_page.ipo_bonds = ipo_bonds
    bond_page.prepare_bonds = prepare_bonds
    bond_page.applying_bonds = applying_bonds
    bond_page.today_bonds = today_bonds
    bond_page.draw_bonds = draw_bonds

    return bond_page

def build_company_brief(stock_code):
    suff_code = crawler.query_stock_suff(stock_code)
    client = ChartClient(False)
    company = client.get_company_info(stock_code + "." + suff_code)
    if company is None:
        log.info("no company data")
        return None
    return company

def build_company(stock_code):
    data = crawler.query_company(stock_code)
    company = CompanyInfo(data)
    if company is None:
        log.info("no company data")
        return None
    return company

def build_similar_bonds(industry_code):
    datas = crawler.query_industry_list(industry_code)
    if datas is None:
        log.info("no similar bonds")
        return None
    similar_bonds = []
    for data in datas:
        cell = data['cell']
        similar_bonds.append(BondData(cell))

    return similar_bonds

def do_generate_similar(bond:BondData):
    line = '**' + bond.bond_name + '**' + '(' + bond.stock_name + ')：' + bond.grade + '评级' '，现价是' + format_func(bond.price) + '，转股价值是' + format_func(bond.convert_value) + '，溢价率是' + format_func(bond.premium_rt) + '%' + '\n'
    return line

def get_main_concept(stock_code:str) -> str:
    df = tushare.concept_detail(stock_code)
    concept_names = df['concept_name'].values.tolist()
    names = filter(lambda name: name not in filter_concept_names, concept_names)
    return '、'.join(names)

def do_generate_prepare_document(prepare:BondInfo, buffers:[], add_finger_print=False, default_estimate_rt=None):

    converter = ImageConverter(prepare.bond_code, prepare.bond_name)
    doms = converter.save(add_finger_print=add_finger_print)
    log.info("save prepare bond image...")

    title = pt.CHAPTER_PREPARE_TITLE.replace('{bond_name}', prepare.bond_name) \
        .replace("{stock_code}", prepare.stock_code) \
        .replace('{bond_code}', prepare.bond_code)

    # 查询相似行业
    industry_code = doms[1]
    industry_text = doms[2]
    similar_bonds = build_similar_bonds(industry_code)
    log.info('query prepare similar bonds...')

    if len(similar_bonds) == 0:
        similar_lines = []
        # 默认30%的溢价率
        estimate_rt = 30.0 if prepare.bond_code not in default_estimate_rt.keys() else default_estimate_rt[prepare.bond_code]
        premium_rt = 100.00 - round(float(prepare.pma_rt), 2)
        estimate_rt_all = round(estimate_rt / 100, 2) + 1
        estimate_amount = round(estimate_rt_all, 2) * round(float(prepare.pma_rt), 2)
    else:
        estimate_amount, \
        estimate_rt, \
        estimate_rt_all, \
        premium_rt, \
        similar_lines = build_estimate_similar(prepare, similar_bonds, default_estimate_rt)

    suff = crawler.query_stock_suff(prepare.stock_code)

    # chart = ChartClient()
    start_date = str(prepare.apply_date).replace('-', '')
    end_date = str(prepare.list_date).replace('-', '')
    chart_data = tushare.get_daily_image(prepare.stock_code + '.' + suff.upper(), prepare.stock_name, start_date, end_date, add_finger_print)

    overview = pt.CHAPTER_PREPARE_OVERVIEW\
        .replace('{bond_code}', prepare.bond_code) \
        .replace('{pic_base64}', (doms[0]).decode()) \
        .replace('{bond_name}', prepare.bond_name) \
        .replace('{list_date}', str(prepare.list_date).replace('2022-', ''))\
        .replace('{apply_date}', str(prepare.apply_date).replace('2022-', ''))\
        .replace('{amount}', format_func(prepare.amount)) \
        .replace('{online_amount}', format_func(prepare.online_amount))\
        .replace('{grade}', prepare.grade) \
        .replace("{valid_apply}", prepare.valid_apply)\
        .replace('{ration_rt}', format_func(round(float(prepare.ration_rt), 2))) \
        .replace('{lucky_draw_rt}', prepare.lucky_draw_rt) \
        .replace('{pma_rt}', format_func(prepare.pma_rt)) \
        .replace('{estimate_rt_all}', format_func(round(estimate_rt_all, 2))) \
        .replace('{estimate_rt}', format_func(round(estimate_rt, 0)))\
        .replace('{estimate_amount}', format_func(round(estimate_amount, 2)))\
        .replace('{stock_old_price}', format_func(chart_data[0]))\
        .replace('{status}', '涨' if chart_data[0] < chart_data[1] else '跌')\
        .replace('{stock_now_price}', format_func(chart_data[1]))\
        .replace('{stock_code}', prepare.stock_code)\
        .replace('{stock_pic_base64}', (chart_data[2]).decode())

    # 插入新数据
    # if trade_open:
    #     model = ApplyBondInfoModel(bond_code=prepare.bond_code, bond_name=prepare.bond_name,
    #                                stock_code=prepare.stock_code, stock_name=prepare.stock_name,
    #                                apply_date=prepare.apply_date, grade=prepare.grade, amount=prepare.amount,
    #                                industry_text=industry_text, list_date=prepare.list_date,
    #                                valid_apply=round(float(prepare.valid_apply), 3), lucky_draw_rt=round(float(prepare.lucky_draw_rt), 3))
    #     sqlclient.update_or_insert_apply_bond_info(model)

    # 简评
    today = date.today()
    tomorrow = (today + timedelta(days=1))
    tomorrow_trade_open = tushare.is_trade_open(tomorrow)
    next_trade_open_day = tushare.next_trade_day(tomorrow)

    briefs.append(pt.CHAPTER_BRIEF_PREPARE_TEXT
                  .replace('{date}', '明日' if tomorrow_trade_open else next_trade_open_day.strftime('%m%d'))
                  .replace('{bond_name}', prepare.bond_name)
                  .replace('{estimate_amount}', format_func(round(estimate_amount, 2))))

    company_info = build_company_brief(prepare.stock_code)
    log.info("query prepare company info...")

    if company_info is None:
        return None

    # 暂时删除公司简介
    # .replace('{gsjj}', company_info['introduction'])\

    company = pt.CHAPTER_PREPARE_COMPANY\
        .replace('{sshy}', industry_text)\
        .replace('{zyyw}', company_info['main_business'])\
        .replace('{hxgn}', get_main_concept(prepare.stock_code))

    buffers.append(title)
    buffers.append(overview)
    buffers.append(pt.CHAPTER_PREPARE_TIPS)
    buffers.append(company)

    if len(similar_lines) != 0:
        buffers.extend(do_generate_apply_company_basic_document(prepare, False))
        buffers.append(pt.CHAPTER_SIMILAR_TEXT)
        for line in similar_lines:
            buffers.append(line)
        buffers.append('\n')

    buffers.append(pt.CHAPTER_NEXT)
    return buffers

def do_generate_apply_company_basic_document(apply:BondInfo, is_show:True) -> []:

    buffers = []

    if is_show:
        basic_data = crawler.query_stock_basic_info(apply.stock_code)
        list_timestamp = basic_data.get('listTime', 0)
        list_date = time.strftime("%Y-%m-%d", time.localtime(list_timestamp / 1000))
        share_total = round(basic_data.get('share_total', 0)/100000000, 2)
        share_liq = round(basic_data.get('share_liq', 0)/100000000, 2)
        total_assets = round(basic_data.get('total_mv', 0), 2)
        pe = basic_data['pepbMap']['pe']
        pe_content = basic_data['pepbMap']['peContent']
        pb = basic_data['pepbMap']['pb']
        pb_content = basic_data['pepbMap']['pbContent']

        # 基本面
        buffers.append(
            pt.CHAPTER_COMPANY_BASIC_SUMMARY
                .replace('{stock_name}', apply.stock_name)
                .replace('{list_date}', list_date)
                .replace('{total_share}', format_func(share_total))
                .replace('{total_assets}', format_func(total_assets))
                .replace('{pe}', format_func(pe))
                .replace('{pe_content}', pe_content.replace('\n', '').replace('😊', '').replace('😰', '').replace('行业：', '').replace('历史：', ''))
                .replace('{pb}', format_func(pb))
                .replace('{pb_content}', pb_content.replace('\n', '').replace('行业：', '').replace('历史：', ''))
        )

    # 业绩
    notice_list = crawler.query_stock_notice(apply.stock_code)
    if len(notice_list) > 0:
        buffers.append(pt.CHAPTER_COMPANY_BASIC_ACHIEVEMENT)
        for data in notice_list:
            type = data['type']
            # 0 预计披露
            if type == 0:
                continue
            # 2 业绩预告
            if type == 2:
                buffers.append('<font color="#1E90FF">' + '**' + data['noticeName'] + '预告：' + data['content'] + '**' + '</font>\n')
                break
            # 1 业绩报告
            if type == 1:
                buffers.append('<font color="#1E90FF">' + '**' + data['noticeName'] + '：' + data['content'] + '**' + '</font>\n')
                break

    if is_show:
        # 亮点
        positive_list = basic_data['comment_new']['positive_new']
        if len(positive_list) > 0:
            buffers.append(pt.CHAPTER_COMPANY_BASIC_POSITIVE)
            for i, data in enumerate(positive_list):
                buffers.append(str(i+1) + '.' + data['value'] + '\n')
        # 风险点
        negative_list = basic_data['comment_new']['unpositive_new']
        if len(negative_list) > 0:
            buffers.append(pt.CHAPTER_COMPANY_BASIC_NEGATIVE)
            for i, data in enumerate(negative_list):
                buffers.append(str(i+1) + '.' + data['value'] + '\n')
    return buffers

def do_generate_apply_document(apply:BondInfo, buffers:[], add_finger_print=False, default_estimate_rt=None, owner_apply_rate:dict=None):
    converter = ImageConverter(apply.bond_code, apply.bond_name)
    doms = converter.save(add_finger_print=add_finger_print)
    log.info("save apply bond image...")

    title = pt.TITLE.replace('{bond_name}', apply.bond_name)\
        .replace("{stock_code}", apply.stock_code)\
        .replace('{bond_code}', apply.bond_code)

    overview = pt.CHAPTER_OVERVIEW\
        .replace('{bond_code}', apply.bond_code)\
        .replace('{pic_base64}', (doms[0]).decode())\
        .replace('{grade}', apply.grade)\
        .replace('{scale}', '小' if apply.amount < 10 else ('还行' if apply.amount < 30 else '大'))\
        .replace('{amount}', format_func(apply.amount))\
        .replace('{stock_name}', apply.stock_name)\
        .replace('{price}', format_func(apply.price))\
        .replace('{convert_price}', format_func(apply.convert_price))\
        .replace('{pma_rt}', format_func(apply.pma_rt))\
        .replace('{purpose}', str(doms[3]).replace('\r', '、'))

    #查询相似行业
    industry_code = doms[1]
    industry_text = doms[2]
    similar_bonds = build_similar_bonds(industry_code)
    log.info('query apply similar bonds...')

    if len(similar_bonds) == 0:
        similar_lines = []
        # 默认30%的溢价率
        estimate_rt = 30.0 if apply.bond_code not in default_estimate_rt.keys() else default_estimate_rt[apply.bond_code]
        premium_rt = 100.00 - round(float(apply.pma_rt), 2)
        estimate_rt_all = round(estimate_rt / 100, 2) + 1
        estimate_amount = round(estimate_rt_all, 2) * round(float(apply.pma_rt), 2)
    else:
        estimate_amount, \
        estimate_rt, \
        estimate_rt_all, \
        premium_rt, \
        similar_lines = build_estimate_similar(apply, similar_bonds, default_estimate_rt)

    # 默认申购股东75%
    pre_apply_rt = owner_apply_rate.get(apply.bond_code, 0.75)

    owner_apply_amount = apply.amount * (1 - pre_apply_rt)
    owner_apply_amount_w = owner_apply_amount * 10000
    estimate_lucky_rt = owner_apply_amount_w/1100/1000
    if estimate_lucky_rt > 0.5:
        lucky_rate = '高'
    elif estimate_lucky_rt > 0.1:
        lucky_rate = '尚可'
    else:
        lucky_rate = '低'

    company_info = build_company(apply.stock_code)
    log.info("query apply company info...")

    if company_info is None:
        return None

    brief_company_info = build_company_brief(apply.stock_code)
    company = pt.CHAPTER_COMPANY_TEXT\
        .replace('{gsmc}', company_info.gsmc)\
        .replace('{sszjhhy}', industry_text)\
        .replace('{hxgn}', get_main_concept(apply.stock_code))\
        .replace('{jyfw}', str(brief_company_info['main_business']).replace(',', '，').replace('.', '。'))

    summary = pt.CHAPTER_SUMMARY\
        .replace('{premium_rt}', format_func(round(premium_rt, 2)))\
        .replace('{grade}', apply.grade)\
        .replace('{estimate_rt}', format_func(round(estimate_rt, 0)))\
        .replace('{convert_value}', format_func(round(float(apply.pma_rt), 2)))\
        .replace('{estimate_rt_all}', format_func(round(estimate_rt_all, 2)))\
        .replace('{estimate_amount}', format_func(round(estimate_amount, 0)))\
        .replace('{owner_apply_rate}', format_func(round(pre_apply_rt * 100, 0)))\
        .replace('{owner_apply_amount}', format_func(round(owner_apply_amount, 2)))\
        .replace('{owner_apply_amount_w}', format_func(round(owner_apply_amount_w, 0)))\
        .replace('{estimate_lucky_rt}', format_func(round(estimate_lucky_rt, 3)))\
        .replace('{lucky_rate}', lucky_rate)

    # 插入新数据
    # if trade_open:
    #     model = ApplyBondInfoModel(bond_code=apply.bond_code, bond_name=apply.bond_name,
    #                                stock_code=apply.stock_code, stock_name=apply.stock_name,
    #                                apply_date=apply.apply_date, grade=apply.grade, amount=apply.amount,
    #                                industry_text=industry_text)
    #     sqlclient.update_or_insert_apply_bond_info(model)
    # 简评
    today = date.today()
    tomorrow = (today + timedelta(days=1))
    next_trade_open_day = tushare.next_trade_day(tomorrow)
    tomorrow_trade_open = tushare.is_trade_open(tomorrow)

    briefs.append(pt.CHAPTER_BRIEF_APPLY_TEXT
                  .replace('{date}', '明日' if tomorrow_trade_open else next_trade_open_day.strftime('%m%d'))
                  .replace('{bond_name}', apply.bond_name)
                  .replace('{estimate_amount}', format_func(round(estimate_amount, 0))))

    buffers.append(title)
    buffers.append(overview)
    buffers.append(company)
    if len(similar_lines) != 0:
        # 公司基本面
        buffers.extend(do_generate_apply_company_basic_document(apply, True))
        buffers.append(pt.CHAPTER_SIMILAR_TEXT)
        for line in similar_lines:
            buffers.append(line)
    buffers.append(summary)
    buffers.append(pt.CHAPTER_NEXT)
    return buffers

def do_compare(bond1:BondData, bond2:BondData) -> int:
    grade_1 = bond1.grade
    grade_2 = bond2.grade
    score_1 = pt.BOND_GRADE_SCORE_MAP.get(grade_1)
    score_2 = pt.BOND_GRADE_SCORE_MAP.get(grade_2)
    if score_1 > score_2:
        return -1
    elif score_1 < score_2:
        return 1
    else:
        return 0

def build_estimate_similar(apply, similar_bonds, default_estimate_rt=None, similar_rank=5):
    # 最大溢价率
    premium_rts = []
    grade_premium_rts = []
    for similar in similar_bonds:
        if similar.grade == apply.grade:
            grade_premium_rts.append(similar.premium_rt)
        premium_rts.append(similar.premium_rt)

    if apply.bond_code in default_estimate_rt.keys():
        estimate_rt = default_estimate_rt[apply.bond_code]
        log.info("query similar bond, assign_premium rate=" + str(estimate_rt))
    elif len(grade_premium_rts) >= 3:
        estimate_rt = np.mean(grade_premium_rts)
        log.info("query similar bond, grade_premium_rts len=" + str(len(grade_premium_rts)) + '; avg=' + str(np.mean(grade_premium_rts)) + "; middle=" + str(np.median(grade_premium_rts)) + "; max=" + str(np.max(grade_premium_rts)) + "; min=" + str(np.min(grade_premium_rts)))
    else:
        estimate_rt = np.mean(premium_rts)
        log.info("query similar bond, premium_rts len=" + str(len(premium_rts)) + '; avg=' + str(np.mean(premium_rts)) + "; middle=" + str(np.median(premium_rts)) + "; max=" + str(np.max(premium_rts)) + "; min=" + str(np.min(premium_rts)))

    similar_lines = []

    similar_bonds.sort(key=cmp_to_key(do_compare), reverse=True)

    is_exceed = len(similar_bonds) > similar_rank
    is_found = False
    rank = 0

    for similar in similar_bonds:
        if is_exceed and apply.grade == similar.grade:
            is_found = True
        if not is_exceed:
            similar_line = do_generate_similar(similar)
            similar_lines.append(similar_line)
        else:
            if is_found and rank < similar_rank:
                similar_line = do_generate_similar(similar)
                similar_lines.append(similar_line)
                rank += 1

    if not is_found and is_exceed:
        filter_similar_bonds = similar_bonds[-similar_rank:]
        for similar in filter_similar_bonds:
            similar_line = do_generate_similar(similar)
            similar_lines.append(similar_line)

    premium_rt = 100.00 - round(float(apply.pma_rt), 2)
    estimate_rt_all = round(estimate_rt / 100, 2) + 1
    estimate_amount = round(estimate_rt_all, 2) * round(float(apply.pma_rt), 2)
    return estimate_amount, estimate_rt, estimate_rt_all, premium_rt, similar_lines


def do_generate_wait_document(wait:BondInfo, is_applying=True):
    if not is_applying:
        line = '<font color="#FF0000" size="2">' + wait.bond_name + '</font>' + '<font size="2">(' + wait.stock_name + ')：' + '发行' + format_func(wait.amount) + '亿元，' + '转股价值' + wait.pma_rt + '，股东配售率是' + format_func(round(float(wait.ration_rt), 2)) + '%' + ('' if wait.list_date is None else '，<font color="#FF0000">**将于' + str(wait.list_date).replace('2022-', '') + '上市**</font></font>') + '\n'
    else:
        line = '<font color="#FF0000" size="2">' + wait.bond_name + '(' + wait.stock_name + ')：' + ' ' + wait.grade + ' 评级，' +  '发行' + format_func(wait.amount) + '亿元，' + '目前转股价值是' + wait.pma_rt + '；' + '将于' + str(wait.apply_date).replace('2022-', '') + '进行申购' + '</font>' + '\n'
    return line

def do_generate_cb_document(cb:BondInfo):
    line = '<font color="#FF0000" size="2">' + cb.stock_name + '</font>' + '<font size="2">：现价' + format_func(cb.price) + '，pb=' + format_func(cb.pb) + '，百元股票含权 ' + format_func(cb.cb_amount) + '元' + '，配售10张所需' + format_func(cb.apply10) + '股；</font>' + '\n'
    return line

def generate_apply_document(apply_bonds, buffers:[], add_finger_print=False, default_estimate_rt=None, owner_apply_rate:dict=None):
    if len(apply_bonds) > 0:
        # 简评
        briefs.append(pt.CHAPTER_BRIEF_APPLY_TITLE)
        for bond in apply_bonds:
            do_generate_apply_document(bond, buffers, add_finger_print, default_estimate_rt, owner_apply_rate)
        briefs.append(pt.CHAPTER_BRIEF_APPLY_TEXT_END)
    return buffers

def generate_prepare_document(prepare_bonds, buffers:[], add_finger_print=False, default_estimate_rt=None):
    if len(prepare_bonds) > 0:
        briefs.append(pt.CHAPTER_BRIEF_PREPARE_TITLE)
        for bond in prepare_bonds:
            do_generate_prepare_document(bond, buffers, add_finger_print, default_estimate_rt)
        briefs.append(pt.CHAPTER_BRIEF_PREPARE_TEXT_END)
    return buffers

def generate_wait_document(ipo_bonds, buffers:[]):

    buffers.append(pt.CHAPTER_WAIT_TEXT)

    for bond in ipo_bonds:
        buffers.append(do_generate_wait_document(bond, is_applying=False))
    return buffers

def generate_applying_document(applying_bonds, buffers:[]):

    if len(applying_bonds) == 0:
        return buffers

    buffers.append(pt.CHAPTER_APPLYING_TEXT)

    for bond in applying_bonds:
        buffers.append(do_generate_wait_document(bond, True))
    return buffers

def generate_cb_document(cb_bonds, buffers:[]):
    buffers.append(pt.CHAPTER_CB_TEXT)
    current = date.today()
    # 查询质押
    mortgage_df = akclient.stock_cg_equity_mortgage_cninfo(current + timedelta(days=-1))

    mortgage_list = []

    for bond in cb_bonds:
        # 如果出现质押的情况，则打印出来
        filter_df = mortgage_df[(mortgage_df['股票代码'] == bond.stock_code)]
        if len(filter_df) > 0:
            mortgage_list.append(bond.stock_code)
            akclient.print_dataframe(filter_df)

        progress_dt = datetime.strptime(bond.progress_dt, "%Y-%m-%d").date()
        diff = current - progress_dt
        if bond.cb_amount > 15 and bond.pb > 0.5 and diff.days <= 90:
            buffers.append(do_generate_cb_document(bond))
    return mortgage_list

def do_generate_dblow_document(row):
    line = pt.DOUBLE_LOW_LINE_TEXT\
        .replace('{bond_name}', row['bond_nm'])\
        .replace('{premium_rt}', str(row['premium_rt']))\
        .replace('{price}', str(row['price']))\
        .replace('{dblow}', str(row['dblow']))\
        .replace('{crr_iss_amount}', format_func(row['curr_iss_amt']))
    return line

def generate_dblow_document(buffers:[]):
    buffers.append(pt.DOUBLE_LOW_TEXT)
    df = crawler.query_bond_data()

    ds = df[(df['price'] <= 120)
            & (df['curr_iss_amt'] >= 0.3)
            & (df['curr_iss_amt'] < 30)
            & (df['year_left'] > 0.5)
            & (df['redeem_icon'] != 'R')
            & (df['redeem_icon'] != 'O')]

    dblow_df = ds.sort_values(by=['dblow'], ascending=[True])
    high = dblow_df.head(10)
    for index, row in high.iterrows():
        buffers.append(do_generate_dblow_document(row))


def do_generate_force_document(force:ForceBondInfo):

    if force.redeem_icon == 'R':
        line = '<font color="#FF0000" size="2">' + force.bond_name + '</font>' + '<font size="2">：最后交易日是' + str(force.redeem_dt).replace('2022-', '') + '，转债现价是' + format_func(force.price) + '元' + '，强赎价是' + format_func(force.real_force_redeem_price) + '元；</font>' + '\n'
    else:
        line = '<font color="#FF0000" size="2">' + force.bond_name + '</font>' + '<font size="2">：转债现价是' + format_func(force.price) + '元，<font color="#FF0000">***公告要强赎。***</font></font>' + '\n'
    return line

def generate_force_document(buffers:[]):

    datas = crawler.query_force_list()

    if len(datas) == 0:
        log.info("no force data...")
        return None

    buffers.append(pt.CHAPTER_FORCE_TEXT)

    suit_datas = []

    for data in datas:
        bond = ForceBondInfo(data)
        if bond.redeem_flag == 'Y':
            buffers.append(do_generate_force_document(bond))
            suit_datas.append(bond)

    bond_names = list(map(lambda x: str(x.bond_name).replace('转债', '').replace('转', ''), suit_datas))

    force_list = '、'.join(bond_names)

    if len(bond_names) > 1:
        briefs.append(pt.CHAPTER_BRIEF_FORCE_TEXT.replace('{force_list}', force_list))
    else:
        briefs.append(pt.CHAPTER_BRIEF_FORCE_SINGLE_TEXT.replace('{force_list}', force_list))

    return buffers

def generate_summary(buffers:[], today_bonds:[], write_simple=False, add_finger_print=False):

    # client = ChartClient()
    data = tushare.get_bond_summary(add_finger_print)
    df = data[0]
    pic_base64 = data[1]

    quote_data = crawler.query_bond_quote()

    sum_amount = df['amount'].sum()

    # 排除今天的上市的转债
    bond_codes = list(map(lambda x: x.bond_code, today_bonds))
    ds = df[~ df['code'].isin(bond_codes)]
    ds = ds.reset_index(drop=True)
    # 降序
    change_sort_df = ds.sort_values(by=['changepercent'], ascending=[False])
    high = change_sort_df.head(3)
    low = change_sort_df.tail(3)
    amplitude_sort_df = df.sort_values(by=['amplitude'], ascending=[False])
    amplitude_high = amplitude_sort_df.head(3)

    le_90_count = quote_data['price_90'] + quote_data['price_90_100']
    gt_130_count = quote_data['price_130']
    line = pt.CHAPTER_BOND_QUOTATION\
        .replace('{total_amount}', format_func(round(sum_amount/100000000, 3)))\
        .replace('{up_count}', str(len(df[df.changepercent > 0])))\
        .replace('{down_count}', str(len(df[df.changepercent < 0])))\
        .replace('{title}', date.today().strftime('%Y-%m-%d'))\
        .replace('{pic_base64}', pic_base64.decode())\
        .replace('{le_90_count}', str(le_90_count))\
        .replace('{gt_130_count}', str(gt_130_count))\
        .replace('{status}', '↓' if str(quote_data['cur_increase_rt']).find('-') != -1 else '↑')\
        .replace('{color}', '#006600' if str(quote_data['cur_increase_rt']).find('-') != -1 else '#FF0000')\
        .replace('{cur_index}', quote_data['cur_index'])\
        .replace('{cur_increase_val}', quote_data['cur_increase_val'])\
        .replace('{cur_increase_rt}', quote_data['cur_increase_rt'])\
        .replace('{ava_price}',quote_data['avg_price'])\
        .replace('{avg_premium_rt}', quote_data['avg_premium_rt'])

    # 统计历史数据
    # if trade_open:
    #     model = BondMarketSummaryModel(total_amount=round(sum_amount/100000000, 3),
    #                                    cur_index=round(float(quote_data['cur_index']), 3),
    #                                    cur_increase_val=round(float(quote_data['cur_increase_val']), 3),
    #                                    cur_increase_rt=round(float(quote_data['cur_increase_rt']), 3),
    #                                    up_count=len(df[df.changepercent > 0]),
    #                                    down_count=len(df[df.changepercent < 0]),
    #                                    avg_price=round(float(quote_data['avg_price']), 3),
    #                                    avg_premium_rt=round(float(quote_data['avg_premium_rt']), 3)
    #                                    )
    #     sqlclient.update_or_insert_bond_market_summary(model)

    buffers.append(line)

    if write_simple:
        high_bond_names = high['name']
        low_bond_names = low['name']
        buffers.append(
            pt.CHAPTER_BOND_QUOTATION_SIMPLE_TEXT \
                .replace('{high}', '、'.join(high_bond_names)) \
                .replace('{high_name}', high.iloc[0]['name']) \
                .replace('{high_rate}', format_func(round(high.iloc[0]['changepercent'], 3))) \
                .replace('{low}', '、'.join(low_bond_names)) \
                .replace('{low_name}', low.iloc[-1]['name']) \
                .replace('{low_rate}', format_func(round(low.iloc[-1]['changepercent'], 3)))
        )

    # 今日上市
    if len(today_bonds) > 0:

        buffers.append(pt.CHAPTER_BOND_QUOTATION_TODAY_TITLE)
        # 简评
        briefs.append(pt.CHAPTER_BRIEF_TODAY_TITLE)

        d_today = df[df['code'].isin(bond_codes)]
        d_today = d_today.reset_index(drop=True)

        for index, row in d_today.iterrows():
            buffers.append(
                pt.CHAPTER_BOND_QUOTATION_TODAY_TEXT
                    .replace('{bond_name}', row['name'])
                    .replace('{open_amount}', format_func(round(row['open'], 3)))
                    .replace('{close_amount}', format_func(round(float(row['trade']), 3)))
            )
            # 简评
            briefs.append(
                pt.CHAPTER_BRIEF_TODAY_TEXT
                    .replace('{bond_name}', row['name'])
                    .replace('{open_amount}', format_func(round(row['open'], 3)))
                    .replace('{close_amount}', format_func(round(float(row['trade']), 3)))
                    .replace('{high_amount}', format_func(round(row['high'], 3)))
            )
            # 更新数据
            # if trade_open:
            #     sqlclient.update_apply_bond_info_price(row['code'],
            #                                        first_day_open_amount=round(row['open'], 3),
            #                                        first_day_close_amount=round(float(row['trade']), 3))

    if not write_simple:
        # 涨幅
        buffers.append(pt.CHAPTER_BOND_QUOTATION_HIGH_TITLE)
        for index, row in high.iterrows():
            stock_code = crawler.query_stock_code(row['code'])
            data = crawler.query_stock_real_price(stock_code)
            buffers.append(
                pt.CHAPTER_BOND_QUOTATION_HIGH_TEXT
                    .replace('{bond_name}', row['name'])
                    .replace('{rate}', format_func(round(row['changepercent'], 3)))
                    .replace('{open_amount}', format_func(round(row['open'], 3)))
                    .replace('{close_amount}', format_func(round(float(row['trade']), 3)))
                    .replace('{zg_rate}', format(round(data['chg'] * 100, 3)))
            )

        # 跌幅
        buffers.append(pt.CHAPTER_BOND_QUOTATION_LOW_TITLE)
        for index, row in low.iterrows():
            stock_code = crawler.query_stock_code(row['code'])
            data = crawler.query_stock_real_price(stock_code)
            buffers.append(
                pt.CHAPTER_BOND_QUOTATION_LOW_TEXT
                    .replace('{bond_name}', row['name'])
                    .replace('{rate}', format_func(round(row['changepercent'], 3)))
                    .replace('{open_amount}', format_func(round(row['open'], 3)))
                    .replace('{close_amount}', format_func(round(float(row['trade']), 3)))
                    .replace('{zg_rate}', format(round(data['chg'] * 100, 3)))
            )

        # 振幅
        buffers.append(pt.CHAPTER_BOND_QUOTATION_AMP_TITLE)
        for index, row in amplitude_high.iterrows():
            buffers.append(
                pt.CHAPTER_BOND_QUOTATION_AMP_TEXT
                    .replace('{bond_name}', row['name'])
                    .replace('{amplitude_rate}', format_func(round(row['amplitude'] * 100, 2)))
                    .replace('{high_amount}', format_func(round(float(row['high']), 3)))
                    .replace('{low_amount}', format_func(round(float(row['low']), 3)))
                    .replace('{close_amount}', format_func(round(float(row['trade']), 3)))
            )

def do_generate_brief(buffers:[], bond:BondInfo, add_finger_print=False, draw_pic=None):

    if bond.bond_code in draw_pic.keys():
        img_path = draw_pic[bond.bond_code]

        # 添加水印
        if add_finger_print:
            fingerprinter.add_finger_print(img_path)

        with open(img_path, 'rb') as f:
            draw_pic_base64 = base64.b64encode(f.read())
    else:
        data = crawler.query_bond_announcement(bond.stock_code)
        anno_list = data['announcements']
        if len(anno_list) == 0:
            log.info('no anno list...')
            return buffers

        # 过滤出最近的公告
        filter_anno_list = []

        for item in anno_list:
            if (datetime.today() - datetime.fromtimestamp(item['announcementTime']/1000)).days <= 5:
                filter_anno_list.append(item)

        draw_result = [ele for ele in filter_anno_list if (str(ele['announcementTitle']).find('中签号码公告') != -1 or str(ele['announcementTitle']).find('中签结果公告') != -1)]
        if len(draw_result) > 0:
            draw_data = draw_result[0]
        else:
            draw_result = [ele for ele in filter_anno_list if str(ele['announcementTitle']).find('中签率及优先配售结果公告') != -1]
            draw_data = None if len(draw_result) == 0 else draw_result[0]

        if draw_data is None:
            return buffers

        pdf_data = pdfutils.get_draw_pdf_table(draw_data['adjunctUrl'], bond.bond_name, add_finger_print)
        draw_pic_base64 = pdf_data[0]

    buffers.append(
        pt.CHAPTER_BRIEF_DRAW_TEXT.replace('{bond_name}', bond.bond_name)
            .replace('{draw_pic_base64}', draw_pic_base64.decode())
            .replace('{ration_rt}', format_func(round(float(bond.ration_rt), 2)))
            .replace('{lucky_draw_rt}', bond.lucky_draw_rt)
            .replace('{single_draw}', bond.single_draw)
            .replace('{sum_count}', str(math.ceil(1/float(bond.single_draw))))
    )

def generate_brief(draw_bonds:[], add_finger_print=False, draw_pic=None):
    if len(draw_bonds) > 0:
        for bond in draw_bonds:
            do_generate_brief(briefs, bond, add_finger_print, draw_pic)
    return briefs

def get_idx_stock(name, rows:[]):
    for row in rows:
        if row['cell']['index_nm'] == name:
            return row['cell']
    return None

def generate_stock_summary():
    idx_data = crawler.query_idx_performance()
    ss_idx = get_idx_stock('上证指数', idx_data)
    sz_idx = get_idx_stock('深证成指', idx_data)
    cy_idx = get_idx_stock('创业板指', idx_data)

    if ss_idx is None or sz_idx is None or cy_idx is None:
        log.info('query idx data failed')
        return

    data = crawler.query_stock_summary()
    briefs.append(pt.CHAPTER_STOCK_SUMMARY_TEXT\
        .replace('{status}', 'FF0000' if data['rise_fall_stat']['r'] > data['rise_fall_stat']['f'] else '006600')\
        .replace('{up}', str(data['rise_fall_stat']['r']))\
        .replace('{down}', str(data['rise_fall_stat']['f']))\
        .replace('{total}', str(data['north_info']['north']))\
        .replace('{hgt_total}', str(data['north_info']['hgt']))\
        .replace('{sgt_total}', str(data['north_info']['sgt']))\
        .replace('{ss_status}', 'FF0000' if float(ss_idx['increase_rt']) > 0 else '006600')\
        .replace('{ss_flag}', '↑' if float(ss_idx['increase_rt']) > 0 else '↓')\
        .replace('{ss_idx}', ss_idx['price'])\
        .replace('{ss_rt}', ss_idx['increase_rt'])\
        .replace('{sz_status}', 'FF0000' if float(sz_idx['increase_rt']) > 0 else '006600') \
        .replace('{sz_flag}', '↑' if float(sz_idx['increase_rt']) > 0 else '↓') \
        .replace('{sz_idx}', sz_idx['price'])\
        .replace('{sz_rt}', sz_idx['increase_rt'])\
        .replace('{cy_status}', 'FF0000' if float(cy_idx['increase_rt']) > 0 else '006600') \
        .replace('{cy_flag}', '↑' if float(cy_idx['increase_rt']) > 0 else '↓') \
        .replace('{cy_idx}', cy_idx['price'])\
        .replace('{cy_rt}', cy_idx['increase_rt'])
        )
    # 统计历史数据
    # if trade_open:
    #     model = StockMarketSummaryModel(ss_idx=round(float(ss_idx['price']),3), ss_rt=round(float(ss_idx['increase_rt']),3),
    #                                     sz_idx=round(float(sz_idx['price']),3), sz_rt=round(float(sz_idx['increase_rt']),3),
    #                                     cy_idx=round(float(cy_idx['price']),3), cy_rt=round(float(cy_idx['increase_rt']),3),
    #                                     up_count=data['rise_fall_stat']['r'], down_count=data['rise_fall_stat']['f'],
    #                                     north_total=data['north_info']['north'], hgt_north_total=data['north_info']['hgt'],
    #                                     sgt_north_total=data['north_info']['sgt'])
    #     sqlclient.update_or_insert_stock_market_summary(model)

def generate_document(title=None, add_head_img=False,
                      generate_blog=False, default_estimate_rt=None,
                      owner_apply_rate:dict=None,
                      draw_pic:dict={},
                      say_something:str='', write_simple=False, add_finger_print=False,
                      write_html=False):
    r""" 生成md文件
    :param owner_apply_rate: 股东默认申购率
    :param add_head_img:
    :param add_finger_print: 是否加水印
    :param generate_blog:
    :param title:
    :param draw_pic: 中签图片路径，因为有时候图片解不出来
    :param write_simple: 是否简略
    :param default_estimate_rt: 默认溢价率
    :param say_something: 想说的简介
    :param write_html:
    :return:
    """
    today = date.today()

    # brief清空
    briefs.clear()

    bond_page = build_bond()
    log.info("build bond...")
    if bond_page is None:
        log.info('no data')
        return None

    apply_bonds = bond_page.apply_bonds
    if len(apply_bonds) == 0:
        log.info("not found apply bond...")
    prepare_bonds = bond_page.prepare_bonds
    #即将上市
    if len(prepare_bonds) == 0:
        log.info("not found prepare bond...")
    log.info('generate prepare data...')

    buffers = []

    # 简评
    briefs.append(pt.CHAPTER_BRIEF_TITLE)
    briefs.append(say_something)
    generate_stock_summary()

    #行情
    generate_summary(buffers, bond_page.today_bonds, write_simple, add_finger_print)
    #上市评测
    generate_prepare_document(prepare_bonds, buffers, add_finger_print, default_estimate_rt)
    #申购评测
    generate_apply_document(apply_bonds, buffers, add_finger_print, default_estimate_rt, owner_apply_rate)

    tags = ['可转债']
    if len(prepare_bonds) > 0 or len(apply_bonds) > 0:
        # briefs.append(pt.CHAPTER_BRIEF_REMARK)
        if len(prepare_bonds) > 0:
            bond_names = list(map(lambda x: str(x.bond_name), prepare_bonds))
            tags += bond_names
        if len(apply_bonds) > 0:
            bond_names = list(map(lambda x: str(x.bond_name), apply_bonds))
            tags += bond_names

    # 简报
    generate_brief(bond_page.draw_bonds, add_finger_print, draw_pic)

    # 即将申购
    log.info('generate applying data...')
    generate_applying_document(bond_page.applying_bonds, buffers)

    mortgage_list = []

    if not write_simple:

        #即将上市
        log.info('generate wait data...')
        generate_wait_document(bond_page.ipo_bonds, buffers)

        log.info('generate force data...')
        # 强赎
        generate_force_document(buffers)
        #含权
        log.info('generate cb data...')
        bond_page.next_bonds.sort(key=lambda bond:bond.cb_amount, reverse=True)
        mortgage_list = generate_cb_document(bond_page.next_bonds, buffers)
        # 双低
        generate_dblow_document(buffers)

    #备注
    # buffers.append(pt.CHAPTER_REMARK)

    head_img_line = '' if not add_head_img else pt.CHAPTER_HEAD_IMAGE_1 \
        .replace('{img_url}', crawler.query_random_img())\
        .replace('{image}', 'img_name')

    final_buffers = [head_img_line] + briefs + buffers

    blog_title = '转债Blog_' + today.strftime('%m%d')  if title is None else title
    # blog_file = blog_title + '.md'
    file_name = '转债_' + today.strftime('%m%d')

    if write_html:
        new_buffers = []
        blog_buffers = []
        # 插入博客标签
        blog_buffers.append(pt.BLOG_HEADER.replace('{title}', blog_title)
                            .replace('{date}', today.strftime('%Y-%m-%d %H:%M:%S'))
                            .replace('{tags}', ', '.join(tags)).replace('{categories}', '可转债打新'))
        for buffer in final_buffers:
            if buffer == '\n' or buffer == '---\n':
                new_buffers.append(buffer)
                continue
            new_buffers.append(buffer.replace('\n', '</br>\n'))
            blog_buffers.append(buffer.replace('&nbsp;', ''))

    with open(file_name + '.md', 'w') as f:
        f.writelines(final_buffers if not write_html else new_buffers)

    # 生成博客
    # if generate_blog and trade_open:
    #     with open(blog_file, 'w') as f:
    #         f.writelines(blog_buffers)
        # shellclient.generate_deploy_blog(blog_file)

    # md转成html
    target_file = mdmaker.md_to_html(file_name)

    # 启动chrome
    # preview.preview('file://' + PROJECT_DIR + '/' + target_file)

    preview_file = today.strftime('%m%d') + '.html'

    shutil.move(target_file, PROJECT_DIR + '/wxcloudrun/templates/' + preview_file)

    os.remove(file_name + '.md')

    return preview_file, mortgage_list

# def main():
#     generate_document(title='通22转债上市，大肉债！申昊转债、科伦转债申购',
#                       add_head_img=False,
#                       generate_blog=False,
#                       default_estimate_rt={'110085': 25.0, '127058': 23, '123142': 27},
#                       owner_apply_rate={},
#                       draw_pic={'127054': '双箭-draw.png'},
#                       add_finger_print=True,
#                       say_something=''
#                                     '1、北向资金结束连续8个交易日的净流出，开始净流入，今天继续普涨行情，3700+上涨；可转债市场成交额再次达到1100亿+规模，这次急速的下跌行情，发现那些溢价率低的可转债还是比较抗跌的；\n'
#                                     '2、湘佳股份公告大股东质押股份，用于认购可转债，感觉应该快发行可转债了，目前百元含权16+；\n'
#                                     '3、天合转债公告要强赎，具体时间未定，目前溢价率-0.13%；\n\n',
#                       write_simple=False,
#                       write_html=True)
#     # 关闭数据库链接
#     sqlclient.close()
#
# if __name__ == '__main__':
#     main()