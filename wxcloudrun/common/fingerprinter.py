#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2022/2/23 4:38 下午
# @Author: zhoumengjie
# @File  : fingerprinter.py
import hashlib
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

def add_finger_print(img_file:str):
    imageInfo = Image.open(img_file)
    resizeImg = imageInfo.resize((1800, 1000))
    resizeImg.save(img_file)

    imageInfo = Image.open(img_file)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Songti.ttc", 50)
    draw = ImageDraw.Draw(imageInfo)
    draw.text((imageInfo.size[0] - 300, 5), u"@一梦想佳", fill=(255, 0, 0), font=font)
    imageInfo.save(img_file)

if __name__ == '__main__':
    # add_finger_print('1.png')
    imageInfo = Image.open('/Users/vandyzhou/Downloads/WechatIMG422.jpg')
    resizeImg = imageInfo.resize((1800, 1000))
    resizeImg.save('/Users/vandyzhou/Downloads/WechatIMG422-1.jpg')