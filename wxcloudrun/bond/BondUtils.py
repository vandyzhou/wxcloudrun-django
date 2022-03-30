#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/8 4:54 下午
# @Author: zhoumengjie
# @File  : BondUtils.py
import json
import logging
import random
import time
import urllib

import pandas as pd
import requests

from wxcloudrun.common import akclient

header = {'Accept': '*/*',
          'Connection': 'keep-alive',
          'Content-type': 'application/json;charset=utf-8',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
          }

cookie = requests.cookies.RequestsCookieJar()
cookie.set('kbzw__user_login', '7Obd08_P1ebax9aXzaPEpdCYrqXR0dTn8OTb3crUja2aqtqr2cPSkavfqKHcnKiYppOprtXdxtPGqqyon7ClmJ2j1uDb0dWMppOkqqefmqekt7e_1KLA59vZzeDapJ6nnJeKw8La4OHs0OPJr5m-1-3R44LDwtqXwsuByIGlqdSarsuui5ai5-ff3bjVw7_i6Ziun66QqZeXn77Atb2toJnh0uTRl6nbxOLmnJik2NPj5tqYsqSlkqSVrqyrppmggcfa28rr1aaXqZilqqk.;')
cookie.set('kbz_newcookie', '1;')
cookie.set('kbzw_r_uname', 'VANDY;')
cookie.set('kbzw__Session', 'fcqdk3pa4tlatoh6c338e19ju2;')

log = logging.getLogger('log')

jisilu_host = 'https://www.jisilu.cn'
cninfo_webapi_host = 'http://webapi.cninfo.com.cn'
east_host = 'https://emweb.securities.eastmoney.com'
zsxg_host = 'https://zsxg.cn'
cninfo_host = 'http://www.cninfo.com.cn'
cninfo_static_host = 'http://static.cninfo.com.cn/'
image_host = 'https://dficimage.toutiao.com'

code_suff_cache = {}

def format_func(num):
    return '{:g}'.format(float(num))

class Crawler:

    def __init__(self, timeout=10):
        self.__timeout = timeout

    def query_list(self):
        r""" 查询待发可转债列表
        :return:
        """
        # 时间戳
        now = time.time()  # 原始时间数据
        timestamp = int(round(now * 1000))
        param = {"___jsl": "LST___t=" + str(timestamp)}
        r = requests.post(jisilu_host + "/data/cbnew/pre_list/", params=param, headers=header, cookies=cookie)
        if r.status_code != 200:
            log.info("查询待发可转债列表失败：status_code = " + str(r.status_code))
            return None
        return r.json()['rows']

    def user_info(self):
        r = requests.post(jisilu_host + '/webapi/account/userinfo/', headers=header, cookies=cookie)
        if r.status_code != 200:
            print("查询集思录用户信息失败：status_code = " + str(r.status_code))
            return False
        data = r.json()
        return data['code'] == 200 and data['data'] is not None

    def login(self):
        h = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        data = 'return_url=' + 'https://www.jisilu.cn/web/data/cb/list' + '&user_name=7d02baf476ca2db25f68cc167b4706a3&password=6a0ed4e2521d177ab76764237b5fc1f3&net_auto_login=1&agreement_chk=agree&_post_type=ajax&aes=1'
        r = requests.post(jisilu_host + '/account/ajax/login_process/', data=data, headers=h, cookies=cookie)
        if r.status_code != 200:
            log.info("登录失败：status_code = " + str(r.status_code))
            return False

        # 重新设置cookies
        cookies = r.cookies.get_dict()
        for key in cookies.keys():
            cookie.set(key, cookies[key])

        # refer
        h = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        r = requests.get(jisilu_host + '/', cookies=cookie, headers=h)
        if r.status_code != 200:
            log.info("登录重定向失败：status_code = " + str(r.status_code))
            return False

        cookies = r.cookies.get_dict()
        for key in cookies.keys():
            cookie.set(key, cookies[key])
        return True

    def query_all_bond_list(self) -> pd.DataFrame:
        r"""
        查询所有已经上市的可转债
        :return:
        """
        # 先判断是否登录，如果没有则登录
        is_login = self.user_info()
        if not is_login:
            print('jisilu no login...')
            is_login = self.login()
            print('jisilu login result:{}'.format(is_login))

        h = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        data = 'btype=C&listed=Y&qflag=N'
        r = requests.post(jisilu_host + "/data/cbnew/cb_list/", headers=h, data=data, cookies=cookie)
        if r.status_code != 200:
            print("查询所有可转债列表失败：status_code = " + str(r.status_code))
            return None
        rows = r.json()['rows']
        df = pd.DataFrame([item["cell"] for item in rows])
        return df

    def query_industry_list(self, industry_code):
        r""" 查询行业可转债列表
        :return:
        """
        # 先判断是否登录，如果没有则登录
        is_login = self.user_info()
        if not is_login:
            log.info('jisilu no login...')
            is_login = self.login()
            log.info('jisilu login result:{}'.format(is_login))
        h = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        #list=Y=仅看已上市
        data = 'sw_cd=' + industry_code + '&listed=Y'
        # fprice=&tprice=&curr_iss_amt=&volume=&svolume=&premium_rt=&ytm_rt=&rating_cd=&is_search=Y&market_cd%5B%5D=shmb&market_cd%5B%5D=shkc&market_cd%5B%5D=szmb&market_cd%5B%5D=szcy&btype=C&listed=N&qflag=N&sw_cd=630303&bond_ids=&rp=50
        r = requests.post(jisilu_host + "/data/cbnew/cb_list_new/", data=data, headers=h, cookies=cookie)
        if r.status_code != 200:
            log.info("查询行业可转债列表失败：status_code = " + str(r.status_code))
            return None
        return r.json()['rows']

    def query_announcement_list(self) -> pd.DataFrame:
        r"""
        查询转债的最新公告
        :return:
        """
        h = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        data = 'code=&title=&tp[0]=Y'
        r = requests.post(jisilu_host + "/webapi/cb/announcement_list/", data=data, headers=h)
        if r.status_code != 200:
            print("查询转债的最新公告失败：status_code = " + str(r.status_code))
            return None
        rows = r.json()['data']
        df = pd.DataFrame(rows)
        return df

    def query_bond_data(self) -> pd.DataFrame:
        r""" 查询交易中的可转债数据
        :return:
        """
        h = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        #list=Y=仅看已上市
        data = 'btype=C&listed=Y&qflag=N'
        # fprice=&tprice=&curr_iss_amt=&volume=&svolume=&premium_rt=&ytm_rt=&rating_cd=&is_search=Y&market_cd%5B%5D=shmb&market_cd%5B%5D=shkc&market_cd%5B%5D=szmb&market_cd%5B%5D=szcy&btype=C&listed=N&qflag=N&sw_cd=630303&bond_ids=&rp=50
        r = requests.post(jisilu_host + "/data/cbnew/cb_list_new/", data=data, headers=h, cookies=cookie)
        if r.status_code != 200:
            log.info("查询交易中的可转债数据：status_code = " + str(r.status_code))
            return None
        rows = r.json()['rows']
        cells = list(map(lambda x: x['cell'], rows))
        df = pd.DataFrame(cells)
        return df

    def query_apply_list(self):
        param = {"history": 'N'}
        r = requests.get(jisilu_host + '/webapi/cb/pre/', params=param, headers=header)
        if r.status_code != 200:
            log.info("查询待发可转债列表失败：status_code = " + str(r.status_code))
            return None
        return r.json()['data']

    def query_bond(self, bond_code):
        r""" 查询转债详情
        :return:
        """
        # 时间戳
        now = time.time()  # 原始时间数据
        timestamp = int(round(now * 1000))
        param = {"___jsl": "LST___t=" + str(timestamp)}
        r = requests.post(jisilu_host + "/data/cbnew/detail_hist/" + bond_code + "/", params=param, headers=header, cookies=cookie)
        if r.status_code != 200:
            log.info("查询可转债详情失败：status_code = " + str(r.status_code))
            return None
        return r.json()['rows']

    def query_idx_performance(self):
        '''
        查询指数情况
        :return:
        '''
        # 时间戳
        now = time.time()  # 原始时间数据
        timestamp = int(round(now * 1000))
        param = {"___jsl": "LST___t=" + str(timestamp)}
        r = requests.post(jisilu_host + "/data/idx_performance/list/", params=param, headers=header,
                          cookies=cookie)
        if r.status_code != 200:
            log.info("查询指数情况：status_code = " + str(r.status_code))
            return None
        return r.json()['rows']

    def query_stock_suff(self, stock_code) -> str:
        r""" 查询所属
        :param stock_code:
        :return:
        """

        suff = 'sh' if stock_code.startswith('6') else 'sz' if stock_code.startswith('0') or stock_code.startswith(
            '3') else 'bj'

        return suff

        # suff = code_suff_cache.get(stock_code)
        #
        # if suff is None:
        #     param = {"text": stock_code}
        #     r = requests.get(zsxg_host + "/api/v2/capital/searchV3", params=param)
        #     if r.status_code != 200:
        #         print("查询股票归属失败：status_code = " + str(r.status_code))
        #         return None
        #     suff = str(r.json()['datas'][0]['codeSuff']).lower()
        #     code_suff_cache[stock_code] = suff
        #     return suff
        # else:
        #     return suff

    def query_stock_basic_info(self, stock_code):
        suff = self.query_stock_suff(stock_code)
        param = {"code": stock_code + '.' + suff.upper(), "yearNum": 2}
        r = requests.get(zsxg_host + "/api/v2/capital/info", params=param)
        if r.status_code != 200:
            log.info("查询股票基本面失败：status_code = " + str(r.status_code))
            return None
        return r.json()['datas']

    def query_stock_real_price(self, stock_code):
        suff = self.query_stock_suff(stock_code)
        body = json.dumps({"codes": stock_code + '.' + suff.upper()})
        r = requests.post(zsxg_host + "/api/v2/capital/realTime", data=body, headers=header)
        if r.status_code != 200:
            log.info("查询股票实时价格失败：status_code = " + str(r.status_code))
            return None
        return r.json()['datas'][0]

    def query_stock_notice(self, stock_code):
        suff = self.query_stock_suff(stock_code)
        param = {"codes": stock_code + '.' + suff.upper()}
        r = requests.get(zsxg_host + "/api/v2/notice/listByCode", params=param)
        if r.status_code != 200:
            log.info("查询股票业绩失败：status_code = " + str(r.status_code))
            return None
        return r.json()['datas']

    def query_stock_summary(self):
        r = requests.get(zsxg_host + "/api/v2/index/northAndRfStat")
        if r.status_code != 200:
            log.info("查询当天交易行情：status_code = " + str(r.status_code))
            return None
        return r.json()['datas']

    def query_company(self, stock_code):
        r""" 查询公司详情
        :param stock_code:
        :return:
        """
        suff = self.query_stock_suff(stock_code)
        param = {"type": 'web', 'code': suff + stock_code}
        r = requests.post(east_host + '/PC_HSF10/CompanySurvey/CompanySurveyAjax', params=param, headers=header,
                          cookies=cookie)
        if r.status_code != 200:
            log.info("查询股票详情失败：status_code = " + str(r.status_code))
            return None
        return r.json()

    def query_force_list(self):
        r = requests.get(jisilu_host + "/webapi/cb/redeem/")
        if r.status_code != 200:
            log.info("查询强赎失败：status_code = " + str(r.status_code))
            return None
        return r.json()['data']

    def query_bond_quote(self):
        r = requests.get(jisilu_host + "/webapi/cb/index_quote/")
        if r.status_code != 200:
            log.info("查询强赎失败：status_code = " + str(r.status_code))
            return None
        return r.json()['data']

    def query_stock_code(self, bond_code):
        org_id = self.query_bond_org_id(bond_code)
        if org_id is None:
            return None
        param = {"bondCode": bond_code, 'orgId': org_id}
        r = requests.get(cninfo_host + "/new/bond/queryOneBond", params=param)
        if r.status_code != 200:
            log.info("根据转债编码查询正股编码失败：status_code = " + str(r.status_code))
            return None
        return r.json()['secCode']

    def query_orgid(self, code):
        param = {"keyWord": code, 'maxNum': 10}
        r = requests.post(cninfo_host + "/new/information/topSearch/query", params=param, headers=header,
                          cookies=cookie)
        if r.status_code != 200:
            log.info("查询org_id失败：status_code = " + str(r.status_code))
            return None
        return r.json()

    def query_stock_org_id(self, stock_code):
        return self.query_orgid(stock_code)[0]['orgId']

    def query_bond_org_id(self, bond_code):
        datas = self.query_orgid(bond_code)
        for data in datas:
            if data['category'] == '可转债':
                return data['orgId']
        return None

    def query_bond_announcement(self, stock_code):
        org_id = self.query_stock_org_id(stock_code)
        if org_id is None:
            return None
        param = {"stock": stock_code + "," + org_id, 'tabName': 'fulltext', 'pageSize': 30, 'pageNum': 1, 'plate': 'bond', 'category': 'category_kzzq_szsh'}
        r = requests.post(cninfo_host + "/new/hisAnnouncement/query", params=param, headers=header,
                          cookies=cookie)
        if r.status_code != 200:
            log.info("查询转债公告列表失败：status_code = " + str(r.status_code))
            return None
        return r.json()

    def query_anno_pdf(self, file_name, path):
        r = requests.get(cninfo_static_host + path)
        if r.status_code != 200:
            log.info("下载文件失败：status_code = " + str(r.status_code))
            return None
        with open(file_name, "wb") as code:
            code.write(r.content)
        return file_name

    def query_random_img(self):
        param = {"from": 0, "size": 100, "term": "风景",
                 "user_id": "58811634363",
                 "media_id": "1721490791634955",
                 "platform": "toutiaohao",
                 "path": "/micro/search",
                 "search_from": "hotword_sug",
                 "position": "article_icstock"}
        r = requests.get(image_host + '/api/proxy/get', params=param)
        if r.status_code != 200:
            log.info("查询图片失败：status_code = " + str(r.status_code))
            return None
        data = r.json()['data']['data']
        hits = data['hits']
        pos = random.randint(0, len(hits))

        return hits[pos]['img']


def main():
    crawler = Crawler()
    # print(crawler.query_anno_pdf('127053.pdf', '/finalpage/2022-01-26/1212274930.PDF'))
    df = crawler.query_all_bond_list()
    # dblow_df = df.sort_values(by=['dblow'], ascending=[True])
    # df['curr_iss_amt'] = df['curr_iss_amt'].map(lambda x: float(x))
    # ds = df[(df['price'] <= 120) & (df['curr_iss_amt'] >= 0.3) & (df['curr_iss_amt'] < 30) & (df['redeem_icon'] != 'R') & (df['redeem_icon'] != 'O')]
    akclient.print_dataframe(df)

if __name__ == '__main__':
    # print(time.strftime("%Y-%m-%d", time.localtime(1569340800000/1000)))
    main()
