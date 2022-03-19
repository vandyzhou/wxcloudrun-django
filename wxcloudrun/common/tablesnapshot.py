#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/1/29 11:51 上午
# @Author: zhoumengjie
# @File  : tablesnapshot.py

import os
import time
from typing import Any

from selenium import webdriver

SNAPSHOT_JS = """
    var ele = document.querySelector('div[_echarts_instance_]');
    var mychart = echarts.getInstanceByDom(ele);
    return mychart.getDataURL({
        type: '%s',
        pixelRatio: %s,
         excludeComponents: ['toolbox']
    });
"""

SNAPSHOT_SVG_JS = """
   var element = document.querySelector('div[_echarts_instance_] div');
   return element.innerHTML;
"""

SNAPSHOT_NONE_JS = """
    var element = document.querySelector('div');
    var mychart = echarts.getInstanceByDom(element);
    return mychart.getDataURL({
        type: '%s',
        pixelRatio: %s,
         excludeComponents: ['toolbox']
    });
"""

def make_snapshot(
    html_path: str,
    file_type: str,
    pixel_ratio: int = 2,
    delay: int = 2,
    browser="Chrome",
    img_type="",
    driver: Any = None,
):
    if delay < 0:
        raise Exception("Time travel is not possible")
    if not driver:
        if browser == "Chrome":
            driver = get_chrome_driver()
        elif browser == "Safari":
            driver = get_safari_driver()
        else:
            raise Exception("Unknown browser!")

    if file_type == "svg":
        snapshot_js = SNAPSHOT_SVG_JS
    else:
        snapshot_js = SNAPSHOT_JS % (file_type, pixel_ratio)

    if img_type == 'table':
        snapshot_js = SNAPSHOT_NONE_JS % (file_type, pixel_ratio)

    if not html_path.startswith("http"):
        html_path = "file://" + os.path.abspath(html_path)

    driver.get(html_path)
    time.sleep(delay)

    # driver.save_screenshot("123.png")

    return driver.execute_script(snapshot_js)


def get_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    return webdriver.Chrome(options=options)


def get_safari_driver():
    return webdriver.Safari()
