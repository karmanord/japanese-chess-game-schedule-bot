#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import boto3
from base64 import b64decode
import sys
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
import requests
import datetime
import json

def drawText(draw,
             text_font_family,
             text_max_font_size, 
             text_color,
             text_height,
             text,
             img_width,
             img_height
             ):

    out_text_size = (img_width + 1, img_height + 1)
    font_size_offset = 0
    font = ImageFont.truetype(text_font_family, text_max_font_size, encoding='utf-8')
    while img_width < out_text_size[0] + 120 or img_height < out_text_size[1]+ 120:
        font = ImageFont.truetype(text_font_family, text_max_font_size - font_size_offset)
        out_text_size = draw.textsize(text, font=font)
        font_size_offset += 1
    w, h = font.getsize(text)
    x = (img_width - w)/2
    y = (img_height - h)/2
    draw.text((x, y + text_height), text, fill=(text_color), font=font)

def postSlackImage(row_list, row_num, ladies_count): 
    if "AbemaTV" in row_list[7] and "ニコニコ" in row_list[7]:
        image_name = "abema-niconico.jpg"
        text_color = "#FFF"
    elif "AbemaTV" in row_list[7]:
        image_name = "abema.jpg"
        text_color = "#FFF"
    elif "ニコニコ" in row_list[7]:
        image_name = "niconico.jpg"
        text_color = "#FFF"
    elif "銀河" in row_list[0]:
        image_name = "ginga.jpg"
        text_color = "#FFF"
    elif "NHK杯" in row_list[0]:
        row_list[0] = "NHK杯将棋トーナメント"
        image_name = "nhk.jpg"
        text_color = "#000"
    elif ladies_count == 2:
        image_name = "ladies.jpg"
        text_color = "#000"
    else:
        image_name = "standart.jpg"
        text_color = "#000"
    img = Image.open(image_name)
    img.filter(ImageFilter.GaussianBlur(10.0))
    draw = ImageDraw.Draw(img)

    img_width = 1920
    img_height = 1278

    text_font_family = 'aoyagireisyosimo_otf_2_01.otf'
    
    players = row_list[2] + "" + row_list[3]  + " - " + row_list[4] + "" + row_list[5]
    drawText(draw, text_font_family, 500, text_color, -300, players, img_width, img_height)

    title =  row_list[0]
    drawText(draw, text_font_family, 100, text_color, 320, title, img_width, img_height)

    img.save('/tmp/upload.jpg', 'JPEG', quality=70, optimize=True)
    files = {'file': open('/tmp/upload.jpg', 'rb')}
    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow_date.strftime("%Y年%m月%d日")
    param = {
        'token': boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['token']))['Plaintext'],
        'channels':boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['images_channel']))['Plaintext'],
        'title': str(tomorrow_str) + ' - 第' + str(row_num) + '組',
    }
    result = requests.post(url="https://slack.com/api/files.upload",params=param, files=files)
    json_data = result.json()
    image_url = json.dumps(json_data["file"]["url_private"])
    return image_url.replace("\"", "")
