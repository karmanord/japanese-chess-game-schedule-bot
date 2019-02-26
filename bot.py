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

ladies_title = ["女流王座", "女流名人", "女流王位", "女流王将", "倉敷藤花", "清麗", "女王"]

h = {"User-Agent":"#"}

tommorow_flg = False
row_num = 1
col_num = 1
ladies_count = 0

row_list = []
all_row_list = []

def getPlayerInfo(tag, row_list):
    
    global ladies_count

    if "中井広恵" in str(tag.text) or "西山朋佳" in str(tag.text) :
        ladies_count += 1

    if "※" in tag.text:
        # LPSA所属棋士に付けられる「※」を除いてリストに追加
        row_list.append(tag.text.strip(" ""※"))
        row_list.append("(LPSA)")
        ladies_count += 1
    elif "＊" in tag.text: 
        # フリー棋士に付けられる「＊」を除いてリストに追加
        row_list.append(tag.text.strip(" ""＊"))
        row_list.append("(フリー)")
    elif "アマ" in tag.text: 
        row_list.append(tag.text.strip("アマ"))
        row_list.append("(アマ)")
    else:
        link = tag.find("a", href=re.compile("^/player/"))
        player_page = requests.get('https://www.shogi.or.jp' + link["href"], headers=h)
        sleep(1)
        player_soup = BeautifulSoup(player_page.content, "lxml") 
        row_list.append(tag.text.strip(" "))
        # 段位・称号をリストに追加
        status = player_soup.select(".headingElementsA01.min.ico03")[0].text.strip(" ")
        if "・" in status:
            status = str(titleCount(status.count("・") + 1).name) + "冠"

        if status in ladies_title:
            ladies_count += 1
        elif status.count("女流"):
            status = status.replace("女流", "") 
            ladies_count += 1
        elif status.count("引退"):
            status = "九段"
        row_list.append(status)

def postSlackMessage(row_list, image_url):

    google_search_url = "https://www.google.com/search?q="
    player1 = urllib.parse.quote(row_list[2] + " 将棋")
    player1 = google_search_url + player1
    
    player2 = urllib.parse.quote(row_list[4] + " 将棋")
    player2 = google_search_url + player2

    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow_date.strftime("%-Y年%-m月%-d日")
    
    tv_type = None
    if "AbemaTV" in row_list[7] and "ニコニコ" in row_list[7]:
        tv_type = 'AbemaTV・ニコニコ生放送'
    elif "AbemaTV" in row_list[7]:
        tv_type = 'AbemaTV'
    elif "ニコニコ" in row_list[7]:
        tv_type = 'ニコニコ生放送'
    elif "銀河" in row_list[0]:
        tv_type = '銀河戦'
    elif "NHK杯" in row_list[0]:
        tv_type = 'NHK杯'

    if tv_type is not None:
        text = '<!channel>\n*' + str(tomorrow_str) + ' - 第' + str(row_num) + '組*'
        fallback = str(tomorrow_str) + "[" + tv_type + "] " + row_list[2] + row_list[3]  + " - " + row_list[4] + row_list[5]
    else:
        text = '*' + str(tomorrow_str) + ' - 第' + str(row_num) + '組*'
        fallback = str(tomorrow_str) + " " + row_list[2] + row_list[3]  + " - " + row_list[4] + row_list[5]
    # Slackに取得した情報を送信する
    payload = {
        "attachments": [
            {
                "fallback": fallback,
                # "color": "#2eb886",
		        "text": text,
                "image_url": image_url,
                "actions": [
                    {
                        "type": "button",
                        "name": "player1",
                        "text": ":mag: " + row_list[2],
                        "url": player1,
                        "style": "normal",
                    },
                    {
                        "type": "button",
                        "name": "player2",
                        "text": ":mag: " + row_list[4],
                        "url": player2,
                        "style": "normal",
                    },
                    {
                        "type": "button",
                        "name": "title",
                        "text": ":mag: " + row_list[0],
                        "url": 'https://www.shogi.or.jp' + row_list[1],
                        "style": "normal",
                    }
                ] 
            }
        ]
    }

    requests.post('#', data=json.dumps(payload))

def irregularPostSlackMessage():
    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow_date.strftime("%-Y年%-m月%-d日")
    payload = {
        "text": str(tomorrow_str) + "は対局予定がありません。"
    }

    requests.post('#', data=json.dumps(payload))

def main():
    deleteMessage.exec()
    # 週間対局予定ページを開く
    r = requests.get('https://www.shogi.or.jp/game/#jsTabE01_02', headers=h)
    soup = BeautifulSoup(r.content, "lxml") # r.textだと文字化けする
    tommorow_day =  str(datetime.datetime.now().day + 1) # 明日の日にちを取得

    for tag in soup.find(id="jsTabE01_02").find_all("td"):
        # 週間対局予定ページの日にち箇所の判定
        if re.search('colspan="5"', str(tag)) is not None:
            global tommorow_flg
            if re.search("月" + tommorow_day + "日|月" + tommorow_day +"・|・" + tommorow_day +"日", str(tag)):
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
                row_list.append(all_row_list[row_num - 2][1])
                getPlayerInfo(tag, row_list)
                col_num += 1
            elif col_num == 1:
                row_list.append(tag.text.strip(" "))
                link = tag.find("a")
                row_list.append(link["href"])
            elif col_num == 2 or col_num == 3:
                getPlayerInfo(tag, row_list)
            # 列番号をリセットする
            elif col_num == 5:
                row_list.append(tag.text.strip(" "))
                all_row_list.append(deepcopy(row_list))
                image_url = picture.postSlackImage(row_list, row_num, ladies_count)
                postSlackMessage(row_list, image_url)
                col_num = 1
                row_num += 1
                ladies_count = 0
                row_list.clear()
                continue
            else:
                row_list.append(tag.text.strip(" "))
            col_num += 1
    if row_num == 1:
        irregularPostSlackMessage()
if __name__ == '__main__':
    main()
