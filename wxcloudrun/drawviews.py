import json
import logging

from django.http import JsonResponse
from django.shortcuts import render

from wxcloudrun import drawquery

logger = logging.getLogger('log')


def index(request, _):
    """
    获取查询页面

     `` request `` 请求对象
    """

    return render(request, 'draw.html')


def query(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """
    return query_draw(request)


def query_draw(request):
    """
    更新计数，自增或者清零

    `` request `` 请求对象
    """

    logger.info('update_count req: {}'.format(request.body))

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    stock_code = body['stockCode']
    apply_no = body['applyNo']

    data = drawquery.query_draw(stock_code, int(apply_no))

    return JsonResponse({'code': 0, "data": data},
                        json_dumps_params={'ensure_ascii': False})
