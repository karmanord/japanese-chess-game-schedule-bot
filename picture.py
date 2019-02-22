#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
import requests
import datetime

def createImage(row_list, count):
    img = Image.open("white.jpg")
    img.filter(ImageFilter.GaussianBlur(4.0))
    draw = ImageDraw.Draw(img)

    img_width = 1920
    img_height = 1278


    #######これと
    out_text_size = (img_width + 1, img_height + 1)
    font_size_offset = 0
    players_fontFile = 'KouzanMouhituFontOTF.otf'
    players_font = ImageFont.truetype(players_fontFile, 300, encoding='utf-8')
    players = row_list[1] + " " + row_list[2]  + " - " + row_list[3] + " " + row_list[4]
    # フォントの描画サイズが描画領域のサイズを下回るまでwhile
    while img_width < out_text_size[0] + 300 or img_height < out_text_size[1]+ 300:
        players_font = ImageFont.truetype(players_fontFile, 150 - font_size_offset)
        # draw.textsizeで描画時のサイズを取得
        out_text_size = draw.textsize(players, font=players_font)
        font_size_offset += 1
    players_w, players_h = players_font.getsize(players)
    players_x = (img_width - players_w)/2
    players_y = (img_height - players_h)/2
    draw.text((players_x, players_y - 350), players, fill=("#000000"), font=players_font)

    #######これが一緒の為メソッドに切り出す
    out_text_size = (img_width + 1, img_height + 1)
    font_size_offset = 0
    title_fontFile = 'KouzanMouhituFontOTF.otf'
    title_font = ImageFont.truetype(title_fontFile, 80, encoding='utf-8')
    title = row_list[0]
    # フォントの描画サイズが描画領域のサイズを下回るまでwhile
    while img_width < out_text_size[0]  + 300 or img_height < out_text_size[1] + 300:
        title_font = ImageFont.truetype(title_fontFile, 80 - font_size_offset)
        # draw.textsizeで描画時のサイズを取得
        out_text_size = draw.textsize(title, font=title_font)
        font_size_offset += 1
    title_w, title_h = title_font.getsize(title)
    title_x = (img_width - title_w)/2
    title_y = (img_height - title_h)/2
    draw.text((title_x, title_y + 420), title, fill=("#000000"), font=title_font)


    # im.show() #即、プレビューする時はここのコメントアウトを外す
    img.save(str(count) + '.jpg', 'JPEG', quality=100, optimize=True)
    files = {'file': open(str(count) + '.jpg', 'rb')}
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow.strftime("%Y年%m月%d日")
    param = {
        'token':"#", 
        'channels':"CGAUB38SU",
        # 'filename': str(count) + '.jpg',
        # 'initial_comment': "initial_comment",
        'title': str(tomorrow) + ' - 第' + str(count) + '組',
    }
    requests.post(url="https://slack.com/api/files.upload",params=param, files=files)