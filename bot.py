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

#ユーザエージェント
h = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
tommorow_flg = False
row_num = 1
col_num = 1
row_list = []
all_row_list = []

def main():
    # 週間対局予定ページを開く
    r = requests.get('https://www.shogi.or.jp/game/#jsTabE01_02', headers=h)
    soup = BeautifulSoup(r.content, "lxml") # r.textだと文字化けする
    tommorow_day =  str(datetime.datetime.now().day + 1) # 明日の日にちを取得
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
            # 棋戦名が他の行とグルーピングされていて存在しない場合、上の行から棋戦名をコピーする
            if col_num == 1 and re.search('class="tac"', str(tag)): 
                row_list.append(all_row_list[row_num - 2][0])
                col_num += 1
            # 列番号をリセットする
            elif col_num == 5:
                row_list.append(tag.text)
                all_row_list.append(deepcopy(row_list))
                print(row_list)
                postSlackMessage(row_list)

                col_num = 1
                row_num += 1
                row_list.clear()
                continue

            # 余計な空白と、LPSA所属およびアマチュア棋士に付けられる「※」を削除する
            row_list.append(tag.text.strip(" ""※"))
            col_num += 1

    

def postSlackMessage(row_list):
    # Slackに取得した情報を送信する
    payload = {
        "attachments": [
            {
                "title": "明日の対局予定",
                "text": row_list[1] + " 対 " +row_list[2] + " (" + row_list[0] +")"
                # "fields": [
                #     {
                #         "title": "報酬金額",
                #         "value": money,
                #         "short": "true"
                #     },
                #     {
                #         "title": "クライアント様(ありがとう数/募集実績数)",
                #         "value": client,
                #         "short": "true"
                #     }
                # ],
            }
            # {
            #     "fallback":task_name,
            #     "color": "#0074C1",
            #     "title": ":ticket:" + task_name,
            #     "title_link": "https://crowdworks.jp/public/jobs/" + str(id),
            #     "fields": [
            #         {
            #             "title": "報酬金額",
            #             "value": money,
            #             "short": "true"
            #         },
            #         {
            #             "title": "クライアント様(ありがとう数/募集実績数)",
            #             "value": client,
            #             "short": "true"
            #         }
            #     ],
            #     "mrkdwn_in": [
            #         "value"
            #     ],
            #     "text": description[0:100] + "...",
            #     "footer": name + ' | ' +str('{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())),
            #     "footer_icon": avatar_url
            # }
        ]
    }

    requests.post('https://hooks.slack.com/services/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', data=json.dumps(payload))                
                
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

if __name__ == '__main__':
    main()