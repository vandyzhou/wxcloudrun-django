import os
from datetime import datetime, date
import json
import logging
import hashlib

from django.http import JsonResponse, HttpResponse, FileResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils.encoding import escape_uri_path

from wxcloudrun import drawquery
from wxcloudrun.bond import jisilu
from wxcloudrun.settings import BASE_DIR

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

def doc_index(request, _):
    """
    生成文档页
    :param request:
    :param _:
    :return:
    """
    path = request.GET.get('docPath', '')
    if len(path) == 0:
        return render(request, 'doc.html')
    else:
        return render(request, path)

def download(request, _):
    """
    下载生成的md文件
    :param request:
    :param _:
    :return:
    """
    filename = request.GET.get('filename', date.today().strftime('%m%d') + '.md')

    filepath = os.path.join(BASE_DIR, 'wxcloudrun', 'static', 'md', filename)

    if not os.path.isfile(filepath):
        return HttpResponse("Sorry but Not Found the File")

    file = open(filepath, 'rb')
    response = StreamingHttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment; filename*=UTF-8''{}".format(escape_uri_path(filename))
    return response

def gen_doc(request, _):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    title = body['title']
    saySomething = body['saySomething'] + '\n\n'
    default_estimate_rt = json.loads(body['default_estimate_rt'] if len(body['default_estimate_rt']) > 0 else "{}")
    owner_apply_rate = json.loads(body['owner_apply_rate'] if len(body['owner_apply_rate']) > 0 else "{}")
    skip_draw_pics = json.loads(body['skip_draw_pics'] if len(body['skip_draw_pics']) > 0 else "[]")

    try:
        data = jisilu.generate_document(title=title,
                      add_head_img=False,
                      default_estimate_rt=default_estimate_rt,
                      skip_draw_pics=skip_draw_pics,
                      owner_apply_rate=owner_apply_rate,
                      draw_pic={},
                      add_finger_print=True,
                      say_something=saySomething,
                      write_simple=False)
        filename = data[0]
        mortgage_list = data[1]
        blogfile = data[2]
        # 下修
        cp_list = data[3][0]
        down_list = data[3][1]
        up_list = data[3][2]

        resp = JsonResponse({'code': 0, "data": filename,
                             "blogfile": blogfile,
                             "mortgages": mortgage_list,
                             "cp_list": cp_list,
                             "up_list": up_list,
                             "down_list": down_list},
                            safe=False)
        # resp['REDIRECT'] = 'REDIRECT'
        return resp
    except Exception as msg:
        logger.error('generate document error:{}'.format(msg))
        resp = JsonResponse({'code': -1, "msg": str(msg)}, safe=False)
        return resp


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
