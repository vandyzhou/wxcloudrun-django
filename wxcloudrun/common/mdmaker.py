#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/14 12:11 下午
# @Author: zhoumengjie
# @File  : MDMaker.py
import os

import markdown

from wxcloudrun.bond.PageTemplate import PROJECT_DIR


def md_to_html(file_name:str):
    source_file = file_name + '.md'
    target_file = file_name + '.html'
    markdown.markdownFromFile(input=source_file, output=target_file, encoding='utf-8')
    decorated_target_file = file_name + "_decorate.html"

    with open(PROJECT_DIR + '/wxcloudrun/common/md.css', 'r') as f:
        md_css = f.read()

    html_texts = []
    with open(target_file, 'r') as f:
        while 1:
            html_text = f.readline()
            if not html_text:
                break
            html_text.replace('\n', '</br>')
            html_texts.append(html_text)

    with open(decorated_target_file, 'w') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html>\n')
        f.write('<head>\n<meta charset="utf-8">\n<style>\n')
        f.write(md_css)
        f.write('</style>\n')
        f.write('<style> @media print{ .hljs{overflow: visible; word-wrap: break-word !important;} }</style>\n</head>\n')
        f.write('<body>\n<div class="markdown-body">\n')
        f.writelines(html_texts)
        f.write('</div>\n</body>\n</html>')

    # 删除html
    os.remove(target_file)

    return decorated_target_file


if __name__ == '__main__':
    md_to_html('../110084')
