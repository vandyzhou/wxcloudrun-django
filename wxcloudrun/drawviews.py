from datetime import datetime
import json
import logging
import hashlib

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from wxcloudrun import drawquery

logger = logging.getLogger('log')

def wechat_validate(request, _):
    logger.info('wechat validate req: {}'.format(request.GET))

    signature = request.GET.get('signature', '')
    timestamp = request.GET.get('timestamp', '')
    nonce = request.GET.get('nonce', '')
    echostr = request.GET.get('echostr', '')
    token = "3edc2wsx1qaz"
    encoding_aes_key = "cnYJGM8Rnrp2Ga79UDg94ZCuDMOHkupbvVOb029F7cO"
    list = [token, timestamp, nonce]
    list.sort()
    sha1 = hashlib.sha1()
    for ele in list:
        sha1.update(ele.encode('utf-8'))
    hashcode = sha1.hexdigest()
    logger.info("wechat validate origin signature:{}, generate signature:{}".format(signature, hashcode))
    if hashcode == signature:
        return HttpResponse(echostr)
    else:
        return HttpResponse("")

def index(request, _):
    """
    首页

     `` request `` 请求对象
    """

    return render(request, 'draw.html')

def query_bond(request, _):

    rows = drawquery.query_apply_list()

    now = datetime.today().date()

    result = []

    for row in rows:
        if row['cb_type'] != '可转债':
            continue
        if row['ap_flag'] == 'C' or row['ap_flag'] == 'E':
            apply_date = datetime.strptime(str(row['apply_date']), '%Y-%m-%d').date()
            diff = (now - apply_date).days
            if diff > 3:
                continue
            data = {"stock_code": row.get('stock_id', '-'), "bond_name": row.get('bond_nm', '-')}
            result.append(data)

    return JsonResponse({'code': 0, "data": result}, safe=False)

def query(request, _):
    """
    查询中签结果

     `` request `` 请求对象
    """
    return query_draw(request)


def query_draw(request):
    """
    查询中签结果

    `` request `` 请求对象
    """

    logger.info('query draw req: {}'.format(request.body))

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    stock_code = body['stockCode']
    apply_no = body['applyNo']

    data = drawquery.query_draw(stock_code, int(apply_no))

    return JsonResponse({'code': 0, "data": data},
                        json_dumps_params={'ensure_ascii': False})
