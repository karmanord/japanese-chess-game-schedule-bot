#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import mysql.connector
import json
import sys
from copy import deepcopy
from time import time
from time import sleep
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import picture

#ユーザエージェント
h = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
tommorow_flg = False
row_num = 1
col_num = 1
row_list = []
all_row_list = []

def getPlayerInfo(tag, row_list):
    if str(tag.text).count("※"):
        # LPSA所属棋士に付けられる「※」を除いてリストに追加
        row_list.append(tag.text.strip(" ""※"))
        row_list.append("(LPSA所属)")
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
        sleep(1)
        player_soup = BeautifulSoup(player_page.content, "lxml") 
        row_list.append(tag.text.strip(" "))
        # 段位・称号をリストに追加
        row_list.append(player_soup.select(".headingElementsA01.min.ico03")[0].text.strip(" "))

def postSlackMessage(row_list):
    # Slackに取得した情報を送信する
    payload = {
        "attachments": [
            {
                "text": row_list[1] + " " + row_list[2]  + " 対 " + row_list[3] + " " + row_list[4]
            }
        ]
    }

    requests.post('#', data=json.dumps(payload))                
                
    # except:
    #     print("例外発生")
    #     import traceback
    #     print(traceback.print_exc())
    # finally:
    #     # カーソル終了
    #     cursor.close()
    #     # MySQL切断
    #     db.close()
    #     # Chromeを完全に切断する
    #     driver.close()
    #     driver.quit()
    #     print('--------------終了--------------')


def main():
    # 週間対局予定ページを開く
    r = requests.get('https://www.shogi.or.jp/game/#jsTabE01_02', headers=h)
    soup = BeautifulSoup(r.content, "lxml") # r.textだと文字化けする
    tommorow_day =  str(datetime.datetime.now().day + 1) # 明日の日にちを取得
    tommorow_day = str(22)

    count = 1
    for tag in soup.find(id="jsTabE01_02").find_all("td"):
        print(str(tag.text))

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
                picture.createImage(row_list, count)
                all_row_list.append(deepcopy(row_list))
                postSlackMessage(row_list)
                count += 1
                col_num = 1
                row_num += 1
                row_list.clear()
                continue
            else:
                row_list.append(tag.text.strip(" "))
            col_num += 1
    print(all_row_list)

if __name__ == '__main__':
    main()