#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/8 7:21 下午
# @Author: zhoumengjie
# @File  : PageTemplate.py
from wxcloudrun.settings import BASE_DIR

PROJECT_DIR=str(BASE_DIR)

BOND_GRADE = ['A-', 'A', 'A+', 'AA-', 'AA', 'AA+', 'AAA-', 'AAA', 'AAA+']

BOND_GRADE_MAP = {1:['A-', 'A', 'A+'], 2:['AA-', 'AA', 'AA+'], 3:['AAA-', 'AAA', 'AAA+']}

BOND_DISTRIBUTE_MAP = {
    '-10+':{'color': '#006000', 'high':-10, 'low': -50},
    '-10':{'color': '#A6FFA6', 'high':-9, 'low': -10},
    '-9':{'color': '#93FF93', 'high':-8, 'low': -9},
    '-8':{'color': '#79FF79', 'high':-7, 'low': -8},
    '-7':{'color': '#53FF53', 'high':-6, 'low': -7},
    '-6':{'color': '#28FF28', 'high':-5, 'low': -6},
    '-5':{'color': '#00EC00', 'high':-4, 'low': -5},
    '-4':{'color': '#00DB00', 'high':-3, 'low': -4},
    '-3':{'color': '#00BB00', 'high':-2, 'low': -3},
    '-2':{'color': '#00A600', 'high':-1, 'low': -2},
    '-1':{'color': '#009100', 'high':0, 'low': -1},
    '平':{'color': '#6C6C6C', 'high':0, 'low': 0},
    '1':{'color': '#CE0000', 'high':1, 'low': 0.001},
    '2':{'color': '#EA0000', 'high':2, 'low': 1},
    '3':{'color': '#FF0000', 'high':3, 'low': 2},
    '4':{'color': '#FF2D2D', 'high':4, 'low': 3},
    '5':{'color': '#FF5151', 'high':5, 'low': 4},
    '6':{'color': '#FF7575', 'high':6, 'low': 5},
    '7':{'color': '#FF9797', 'high':7, 'low': 6},
    '8':{'color': '#FFB5B5', 'high':8, 'low': 7},
    '9':{'color': '#FFD2D2', 'high':9, 'low': 8},
    '10':{'color': '#930000', 'high':10, 'low': 9},
    '10+':{'color': '#750000', 'high':50, 'low': 10}
}

BOND_GRADE_SCORE_MAP = {'B-':-6, 'B':-5, 'B+':-4, 'BB-':-3, 'BB':-2, 'BB+':-1, 'A-':0, 'A':1, 'A+': 2, 'AA-':3, 'AA':4, 'AA+':5, 'AAA-':6, 'AAA':7, 'AAA+':8}

BLOG_HEADER = '---\n' \
              + 'title: {title}\n' \
              + 'date: {date}\n' \
              + 'tags: [{tags}]\n' \
              + 'categories: {categories}\n' \
              + '---\n'

CHAPTER_PREPARE_TITLE = '#### 新债上市 {bond_name}（正股代码：{stock_code}，债券代码：{bond_code}）\n'

TITLE = '#### 新债申购 {bond_name}（正股代码：{stock_code}，债券代码：{bond_code}）\n'

CHAPTER_HEAD_IMAGE = '![{image}](data:image/jpg;base64,{img_base64})\n'
CHAPTER_HEAD_IMAGE_1 = '<img src="{img_url}" alt="{image}" width="720" height="270" align="center" />\n'

CHAPTER_PREPARE_OVERVIEW = \
    '#### 转债概况 \n' \
    + '![{bond_code}](data:image/png;base64,{pic_base64})\n' \
    + '![{stock_code}](data:image/png;base64,{stock_pic_base64})'\
    + '**<font color="#FF0000">{bond_name} 将于 {list_date} 上市</font>，{grade} 级别，总规模 {amount} 亿，网上规模 {online_amount} 亿，原始股东配售率 {ration_rt}%，申购账户共{valid_apply}万户，单账户顶格申购中{lucky_draw_rt}签；**\n' \
    + '**转债条款**：到期税前收益（{before_benefit}），税后收益（{after_benefit}），下修条款（{down_rate}），赎回条款（{redeem_rate}），回售条款（{resale_rate}）。\n' \
    + '**个人看法**：截止到今天收盘，股价从申购日（{apply_date}）的 {stock_old_price} **{status}到了** 如今的 {stock_now_price}，综合之前测评，结合当前环境给予 {estimate_rt}% 的溢价率，<font color="#FF0000">上市价格预测：{pma_rt}\\*{estimate_rt_all}={estimate_amount}。</font>\n\n'\
    + '<font color="#FF0000">***以上观点仅为个人看法，所涉标的不作推荐，投资有风险，入市需谨慎。***</font>\n'

CHAPTER_PREPARE_OVERVIEW_SUMMARY = '{bond_name}将于{list_date}上市，{grade}级别，总规模{amount}亿，综合之前测评，结合当前环境给予{estimate_rt}% 的溢价率，上市价格预测：{estimate_amount}，恭喜中签的小伙伴吃肉；'

# + '**公司简介**：{gsjj}\n'\
CHAPTER_PREPARE_COMPANY = '#### 公司概况\n' \
                          + '**主营业务**：{zyyw}\n'\
                          + '**所属行业**：{sshy}\n' \
                          + '**核心概念**：{hxgn}\n'

CHAPTER_PREPARE_TIPS = '> <font size="2">沪市转债集合竞价区间70-150，涨幅超过30%停牌至下午2：57；</font>\n' \
                       + '> <font size="2">深市转债集合竞价区间70-130，涨幅超20%停牌半小时，涨30%直接停盘至下午2点57；</font>\n'

CHAPTER_OVERVIEW = \
    '#### 发行概况 \n' \
    + '![{bond_code}](data:image/png;base64,{pic_base64})' \
    + '**评级**：{grade}评级，可转债评级越高越好。\n' \
    + '**发行规模**：{amount}亿，规模{scale}，可转债规模越大流动性越好。\n' \
    + '**转股价值**：{stock_name}今日收盘价{price}，转股价{convert_price}，转股价值=转债面值/转股价\\*正股价格=100/{convert_price}\\*{price}={pma_rt}，可转债转股价值越高越好。\n' \
    + '**转债条款**：到期税前收益（{before_benefit}），税后收益（{after_benefit}），下修条款（{down_rate}），赎回条款（{redeem_rate}），回售条款（{resale_rate}）。\n' \
    + '**募资用途**：{purpose}\n'

CHAPTER_OVERVIEW_SUMMARY = '{bond_name}将于明天申购，当前溢价率{premium_rt}%，结合{grade}评级、{amount}亿元规模、相似的转债、正股质地等综合因素目前给予{estimate_rt}%的溢价率，预计{estimate_amount}上市，我将顶格申购；祝大家多多中签；'

CHAPTER_SIMILAR_TEXT = \
    '#### 相似转债\n'

CHAPTER_COMPANY_TEXT = \
    '#### 公司简介\n'\
    + '**公司名称**：{gsmc}\n' \
    + '**所属行业**：{sszjhhy}\n' \
    + '**核心概念**：{hxgn}\n' \
    + '**主营业务**：{jyfw}\n'

CHAPTER_COMPANY_BASIC_SUMMARY = '**基本面**：{stock_name}于{list_date}上市，共发行{total_share}亿股，总市值{total_assets}亿元，<font color="#1E90FF">**市盈率{pe}**</font>，<font color="#FF0000">{pe_content}</font><font color="#1E90FF">**市净率{pb}**</font>，<font color="#FF0000">{pb_content}</font>\n'
CHAPTER_COMPANY_BASIC_ACHIEVEMENT = '**业绩情况**：'
CHAPTER_COMPANY_BASIC_POSITIVE = '<font color="#006600">**亮点**</font>：\n'
CHAPTER_COMPANY_BASIC_NEGATIVE = '<font color="#FF0000">**风险点**</font>：\n'


CHAPTER_SUMMARY = \
    '#### 个人看法\n' \
    + '<font color="#FF0000">**当前溢价率{premium_rt}%，结合{grade}评级、相似的转债、正股质地等综合因素目前给予{estimate_rt}%的溢价率，预计价值：{convert_value}\\*{estimate_rt_all}={estimate_amount}；我会申购。**</font>\n' \
    + '假设原始股东配售{owner_apply_rate}%，网上申购按{owner_apply_amount}亿计算，顶格申购单账户中约{owner_apply_amount_w}/1100/1000={estimate_lucky_rt}签，中签率{lucky_rate}。\n\n' \
    + '<font color="#FF0000">***以上观点仅为个人看法，所涉标的不作推荐，投资有风险，入市需谨慎。***</font>\n'

CHAPTER_NEXT = '---\n'

CHAPTER_WAIT_TEXT = \
    '##### 即将上市新债\n' \
    + '<font size="2">**新债发行流程：董事会预案 → 股东大会批准 → 证监会受理 → 发审委通过 → 证监会核准/同意注册 → 发行公告**</font>\n'\

CHAPTER_APPLYING_TEXT = \
    '##### 即将申购新债\n'

CHAPTER_CB_TEXT = '##### 含权排名\n'

DOUBLE_LOW_TEXT = '##### 双低排名\n'
DOUBLE_LOW_LINE_TEXT = '<font size="2"><font color="#FF0000">{bond_name}</font>：现价{price}，溢价率{premium_rt}%，双低值{dblow}，剩余规模{crr_iss_amount}亿</font>\n'

CHAPTER_FORCE_TEXT = \
    '##### 强赎\n' \

CHAPTER_FORCE_SUMMARY = '目前多只转债（{force_list}）公布强赎，如果不要转股的话，大家记得不要忘记操作；'

CHAPTER_BOND_QUOTATION = '#### 转债市场行情\n' \
                         + '![{title}](data:image/png;base64,{pic_base64})'\
                         + '今天沪深可转债共成交 {total_amount} 亿元；其中<font color="#FF0000">**上涨共{up_count}只**</font>，<font color="#006600">**下跌共{down_count}只**</font>；<font color="#1E90FF">**低于100元共 {le_90_count}只**，**130+元共 {gt_130_count}只**</font>；\n' \
                           '转债等权指数：<font color="{color}">**{cur_index} {status} \\[{cur_increase_val}, {cur_increase_rt}%\\]**</font>，**平均价格{ava_price}，转股溢价率{avg_premium_rt}**。\n'

CHAPTER_BOND_QUOTATION_SIMPLE_TEXT = '<font color="#FF0000">涨幅前三的依次是：{high}，其中{high_name}以{high_rate}%的涨幅领先；</font><font color="#006600">而跌幅前三的依次是：{low}，其中{low_name}跌幅最大，达到{low_rate}%；</font>\n'

CHAPTER_BOND_QUOTATION_TODAY_TITLE = '<font color="#000079">**今日上市：**</font>\n'
CHAPTER_BOND_QUOTATION_TODAY_TEXT = '&nbsp;&nbsp;&nbsp;&nbsp;<font color="#000079">{bond_name}</font>（开盘{open_amount}，收于{close_amount}）\n'
CHAPTER_BOND_QUOTATION_HIGH_TITLE = '<font color="#FF0000">**涨幅前三：**</font>\n'
CHAPTER_BOND_QUOTATION_HIGH_TEXT = '&nbsp;&nbsp;&nbsp;&nbsp;<font color="#FF0000">{bond_name}</font>（涨幅{rate}%，开盘{open_amount}，收于{close_amount}；正股涨跌{zg_rate}%）\n'
CHAPTER_BOND_QUOTATION_LOW_TITLE = '<font color="#006600">**跌幅前三：**</font>\n'
CHAPTER_BOND_QUOTATION_LOW_TEXT = '&nbsp;&nbsp;&nbsp;&nbsp;<font color="#006600">{bond_name}</font>（跌幅{rate}%，开盘{open_amount}，收于{close_amount}；正股涨跌{zg_rate}%）\n'
CHAPTER_BOND_QUOTATION_AMP_TITLE = '<font color="#1E90FF">**振幅前三：**</font><font size="2">振幅=(最高价-最低价)/开盘价</font>\n'
CHAPTER_BOND_QUOTATION_AMP_TEXT = '&nbsp;&nbsp;&nbsp;&nbsp;<font color="#1E90FF">{bond_name}</font>（振幅{amplitude_rate}%，最高{high_amount}，最低{low_amount}，收于{close_amount}）\n'

CHAPTER_BRIEF_TITLE = "#### 简评\n"
CHAPTER_BRIEF_DRAW_TEXT = '<font color="#FF0000">**{bond_name}中签结果：**</font>\n' \
                     '股东配售率是{ration_rt}%，网上中签率{lucky_draw_rt}%，顶格申购单户中{single_draw}签，<font color="#FF0000">**{sum_count}中1**</font>\n' \
                     '![{bond_name}](data:image/png;base64,{draw_pic_base64})\n'

CHAPTER_BRIEF_TODAY_TITLE = '<font color="#FF0000">**今日上市：**</font>\n'
CHAPTER_BRIEF_TODAY_TEXT = '<font color="#1E90FF">{bond_name}</font> 今天上市，开盘{open_amount}，最高{high_amount}，最终收于{close_amount}；\n'

CHAPTER_BRIEF_PREPARE_TITLE = '<font color="#FF0000">**上市提醒：**</font>\n'
CHAPTER_BRIEF_PREPARE_TEXT = '<font color="#1E90FF">{bond_name}</font> {date}上市，上市价格预测 {estimate_amount}；\n'
CHAPTER_BRIEF_PREPARE_TEXT_END = '恭喜中签的小伙伴吃肉~ <font size="2" color="#000079">*详细测评见下文~*</font>\n'

CHAPTER_BRIEF_APPLY_TITLE = '<font color="#FF0000">**申购提醒：**</font>\n'
CHAPTER_BRIEF_APPLY_TEXT = '<font color="#1E90FF">{bond_name}</font> {date}申购，预计{estimate_amount}上市，我会申购；\n'
CHAPTER_BRIEF_APPLY_TEXT_END = '希望大家多多中签~ <font size="2" color="#000079">*详细测评见下文~*</font>\n'

CHAPTER_BRIEF_FORCE_TEXT = '<font color="#FF0000">**\n强赎提醒：目前多只转债（{force_list}）已经公布强赎，强赎最后交易日见下文；**</font>\n'
CHAPTER_BRIEF_FORCE_SINGLE_TEXT = '<font color="#FF0000">**\n强赎提醒：目前{force_list}已经公布强赎，强赎最后交易日见下文；**</font>\n'

CHAPTER_STOCK_SUMMARY_TEXT = '<font color="#FF0000">**今日股市涨跌统计：**</font>\n' \
                             '**上证指数 <font color="#{ss_status}">{ss_idx} {ss_flag}\\[{ss_rt}%\\]</font>，深证成指 <font color="#{sz_status}">{sz_idx} {sz_flag}\\[{sz_rt}%\\]</font>，创业板指 <font color="#{cy_status}">{cy_idx} {cy_flag}\\[{cy_rt}%\\]</font>**\n'\
                             '<font color="#{status}">**其中上涨共{up}只，下跌共{down}只；两市总成交额{total_deal_money}亿元，北向资金总净流入{total}亿元，沪股通净流入{hgt_total}亿元，深股通净流入{sgt_total}亿元；**</font>\n'

CHAPTER_INDUSTRY_TEXT = '<font color="#FF0000">**领涨行业：**</font>{industry_up}；<font color="#006600">**领跌行业：**</font>{industry_down}\n'
CHAPTER_CONCEPT_TEXT = '<font color="#FF0000">**领涨概念：**</font>{concept_up}；<font color="#006600">**领跌概念：**</font>{concept_down}\n\n'

CHAPTER_IMAGE_TEXT = '![{title}](data:image/png;base64,{draw_pic_base64})\n'
CHAPTER_DBLOW_HEADER = ['转债名称', '现价', '溢价率', '双低值', '剩余规模']

CHAPTER_BRIEF_REMARK = '<font size="2" color="#000079">*详细测评见下文~*</font>\n\n'

CHAPTER_REMARK = '> 以上数据均来自[集思录](http://jisilu.cn/)\n'