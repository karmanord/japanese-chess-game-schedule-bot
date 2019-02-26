#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import json
import sys
from copy import deepcopy
from time import time
from time import sleep
import datetime
import urllib.parse

import picture
import deleteMessage

from enum import Enum

class titleCount(Enum):
    一 = 1
    二 = 2
    三 = 3
    四 = 4
    五 = 5
    六 = 6
    七 = 7
    八 = 8


#ユーザエージェント
h = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}

tommorow_flg = False
row_num = 1
col_num = 1
ladies_count = 0

row_list = []
all_row_list = []

def getPlayerInfo(tag, row_list):
    
    global ladies_count

    if str(tag.text).count("中井広恵") or str(tag.text).count("西山朋佳") :
        ladies_count += 1

    if str(tag.text).count("※"):
        # LPSA所属棋士に付けられる「※」を除いてリストに追加
        row_list.append(tag.text.strip(" ""※"))
        row_list.append("(LPSA)")
        ladies_count += 1
    elif str(tag.text).count("＊"): 
        # フリー棋士に付けられる「＊」を除いてリストに追加
        row_list.append(tag.text.strip(" ""＊"))
        row_list.append("(フリー)")
    elif str(tag.text).count("アマ"): 
        row_list.append(tag.text.strip("アマ"))
        row_list.append("(アマ)")
    else:
        link = tag.find("a", href=re.compile("^/player/"))
        player_page = requests.get('https://www.shogi.or.jp' + link["href"], headers=h)
        # print(1)
        sleep(1)
        player_soup = BeautifulSoup(player_page.content, "lxml") 
        row_list.append(tag.text.strip(" "))
        # 段位・称号をリストに追加
        status = player_soup.select(".headingElementsA01.min.ico03")[0].text.strip(" ")
        if status.count("・"):
            status = str(titleCount(status.count("・") + 1).name) + "冠"

        if status.count("女流王座") or status.count("女流名人") or status.count("女流王位") or status.count("女流王将") or status.count("倉敷藤花") or status.count("清麗") or status.count("女王"):
            ladies_count += 1
        elif status.count("女流"):
            status = status.replace("女流", "") 
            ladies_count += 1
        elif status.count("引退"):
            status = "九段"
        row_list.append(status)

def postSlackMessage(row_list, image_url):
    base_url = "https://www.google.com/search?q="
    player1 = urllib.parse.quote(row_list[1] + " 将棋")
    player1 = base_url + player1
    
    player2 = urllib.parse.quote(row_list[3] + " 将棋")
    player2 = base_url + player2

    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow_date.strftime("%-Y年%-m月%-d日")
    # Slackに取得した情報を送信する
    payload = {
        "attachments": [
            {
                "fallback": "",
                "color": "#2eb886",
		        "text":  "*" + str(tomorrow_str) + ' - 第' + str(row_num) + '組*',
                "image_url": image_url,
                "actions": [
                    {
                        "type": "button",
                        "name": "player1",
                        "text": ":mag: " + row_list[1],
                        "url": player1,
                        "style": "normal",
                    },
                    {
                        "type": "button",
                        "name": "player2",
                        "text": ":mag: " + row_list[3],
                        "url": player2,
                        "style": "normal",
                    }
                ] 
            }
        ]
    }

    requests.post('#', data=json.dumps(payload))

def main():
    deleteMessage.exec()
    # 週間対局予定ページを開く
    r = requests.get('https://www.shogi.or.jp/game/#jsTabE01_02', headers=h)
    soup = BeautifulSoup(r.content, "lxml") # r.textだと文字化けする
    tommorow_day =  str(datetime.datetime.now().day + 1) # 明日の日にちを取得
    # tommorow_day = str(1)

    for tag in soup.find(id="jsTabE01_02").find_all("td"):
        # 週間対局予定ページの日にち箇所の判定
        if re.search('colspan="5"', str(tag)) is not None:
            global tommorow_flg
            if re.search("(?<=月)" + tommorow_day + "|(?<=・)" + tommorow_day, str(tag)):
                tommorow_flg = True
                continue
            else:
                tommorow_flg = False
                continue

        if tommorow_flg:
            global row_num
            global col_num
            global ladies_count
            # 棋戦名が他の行とグルーピングされていて存在しない場合、上の行から棋戦名をコピーする
            if col_num == 1 and re.search('class="tac"', str(tag)): 
                row_list.append(all_row_list[row_num - 2][0])
                getPlayerInfo(tag, row_list)
                col_num += 1
            elif col_num == 2 or col_num == 3:
                getPlayerInfo(tag, row_list)
            # 列番号をリセットする
            elif col_num == 5:
                row_list.append(tag.text.strip(" "))
                if row_num == 1:
                    row_list[6] = "AbemaTV"
                elif row_num == 2:
                    row_list[6] = "ニコニコ"
                elif row_num == 3:
                    row_list[6] = "ニコニコAbemaTV"
                elif row_num == 4:
                    row_list[0] = "銀河戦 Aブロック"
                elif row_num == 5:
                    row_list[0] = "NHK杯"

                all_row_list.append(deepcopy(row_list))
                image_url = picture.postSlackImage(row_list, row_num, ladies_count)
                postSlackMessage(row_list, image_url)
                #break
                col_num = 1
                row_num += 1
                ladies_count = 0
                row_list.clear()
                continue
            else:
                row_list.append(tag.text.strip(" "))
            col_num += 1

if __name__ == '__main__':
    main()
