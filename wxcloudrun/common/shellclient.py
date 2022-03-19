#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/2/12 7:09 下午
# @Author: zhoumengjie
# @File  : shellclient.py
import subprocess

from wxcloudrun.bond.PageTemplate import PROJECT_DIR


def generate_deploy_blog(markdown_file):
    p = subprocess.Popen(args=[PROJECT_DIR + '/common/blog.sh ' + markdown_file], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        print(p.stdout.readline())

if __name__ == '__main__':
    generate_deploy_blog('render.html')