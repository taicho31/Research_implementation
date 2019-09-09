# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import time
from bs4 import BeautifulSoup
import pandas as pd
import urllib

RA=5036765
CA=37
RB=129843
CB=32
RC=13268
CC=37
RE=3456
CE=41
RD=54603
CD=33
I=12
T=2
W=4
S=70
R1=10
R2=2
R3=2
B1=9
B2=9
UNCHECK=-1
TNAME=9
TRESULT=9
BNAME=9
BRESULT=9

omote=np.zeros((TNAME,TRESULT))
ura=np.zeros((BNAME,BRESULT))
table=np.ones((I,T,W,S,R1,R2,R3,B1,B2)) * UNCHECK
btable=np.ones((I,T,W,S,R1,R2,R3,B1,B2)) * UNCHECK
stable=np.zeros((I,T,W,S,R1,R2,R3,B1,B2), dtype="unicode")

giants_bat_url = "https://baseballdata.jp/1/ctop.html"
swallows_bat_url = "https://baseballdata.jp/2/ctop.html"
dena_bat_url = "https://baseballdata.jp/3/ctop.html"
dragons_bat_url = "https://baseballdata.jp/4/ctop.html"
tigers_bat_url = "https://baseballdata.jp/5/ctop.html"
carp_bat_url = "https://baseballdata.jp/6/ctop.html"

lions_bat_url = "https://baseballdata.jp/7/ctop.html"
fighters_bat_url = "https://baseballdata.jp/8/ctop.html"
lotte_bat_url = "https://baseballdata.jp/9/ctop.html"
orix_bat_url = "https://baseballdata.jp/11/ctop.html"
softbank_bat_url = "https://baseballdata.jp/12/ctop.html"
eagles_bat_url = "https://baseballdata.jp/376/ctop.html"

def data_generate(URL):
    html = urllib.request.urlopen(URL)

    # htmlをBeautifulSoupで扱う
    soup = BeautifulSoup(html, "html.parser")

    all_row = soup.tbody.findAll("tr")
    row_tmp = all_row[0].getText().replace("\r", "").replace(" ", "").split("\n")
    row = [a for a in row_tmp if a != '']
    print("contents, length: {} {}".format(row, len(row)))

    data = soup.findAll("td")
    tmp = []
    df = pd.DataFrame()
    for i in range(len(data)):
        ch = data[i].getText().replace("\n", "").replace("\r", "").replace(".---", "").replace(" ", "")
        tmp.append(ch)

    for i in range(int(len(tmp)/39)):
        ind_data = pd.DataFrame([tmp[39*i:39*i+39]], columns=row)
        df = pd.concat([df, ind_data], axis=0)

    team = df.iloc[0]["球団"]
    print(team)

    # データの型をobject型からint、またはfloat型に変換する
    for i in ["打点", "本塁打", "安打数", "単打", "2塁打", "3塁打", "得点圏打数", "得点圏安打", "UC本塁打", "試合数", "打席数", "打数", "得点",
          "四球", "死球", "企盗塁", "盗塁", "企犠打","犠打", "犠飛", "代打数", "代打安打", "併殺", "失策", "三振"]:
        df[i] = df[i].astype("int")

    for i in ["打率", "出塁率", "長打率", "最近5試合", "OPS", "得点圏打率", "UC率"]:
        df[i] = df[i].astype("float")

    df["盗塁成功率"] = df["盗塁"] / df["企盗塁"]
    df["犠打成功率"] = df["犠打"] / df["企犠打"]
    df["代打率"] = df["代打安打"] / df["代打数"]

    # 欠損値は0で補完
    df["盗塁成功率"].fillna(0, inplace=True)
    df["犠打成功率"].fillna(0, inplace=True)

    #　選手名を修正
    players = []
    for i in range(df.shape[0]):
        players.append(df.iloc[i]["選手名"].split(":")[1].split(".")[0].split(team)[0])
    df["選手名"] = players

    # 各選手について 凡退,単打率 二塁打率 三塁打率 本塁打率 四死球率 盗塁成功率 犠打成功率　併殺打率を計算する
    cal_list = ["選手名", "凡退率", "単打率", "2塁打率", "3塁打率", "本塁打率", "四死球率", "盗塁成功率", "犠打成功率", "併殺打率"]
    df["単打率"] = df["単打"] / (df["打席数"] - df["犠打"])
    df["2塁打率"] = df["2塁打"] / (df["打席数"] - df["犠打"])
    df["3塁打率"] = df["3塁打"] / (df["打席数"] - df["犠打"])
    df["本塁打率"] = df["本塁打"] / (df["打席数"] - df["犠打"])
    df["四死球率"] = (df["四球"] + df["死球"]) / (df["打席数"] - df["犠打"])
    df["併殺打率"] = df["併殺"] / (df["打席数"] - df["犠打"])
    df["凡退率"] = 1 - df["出塁率"]

    # 計算に使用する変数だけ抽出
    calc_df = df[cal_list]
    return calc_df

# -----------------------
# イニング, 表裏, アウトカウント, 点差, 一塁走者, 二塁走者, 三塁走者, 打順, 先攻チーム選手の攻撃力、後攻チーム選手の攻撃力
# インデックスにマイナスをつけられないので、35点を同点とし、それ以上が先行リード、それ以下が後攻リードとした。
def calc(i, t, w, s, r1, r2, r3, b1, b2, omote, ura):
    b1 = b1 % 9
    b2 = b2 % 9
    t = t % 2
    if w > 3:
        w = 3
    # a: 併殺打
    # b: 盗塁
    # c: 犠打
    # d: 犠打なし
    # e: 敬遠
    # f: 併殺打で0点

    if table[i][t][w][s][r1][r2][r3][b1][b2] != UNCHECK:
        return table[i][t][w][s][r1][r2][r3][b1][b2]

    elif i >= 8 and t == 1 and w == 3 and s > 35:
        stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
        table[i][t][w][s][r1][r2][r3][b1][b2] = 1

    elif ((i == 8 and t == 0 and w == 3 and s < 35) or (i >= 8 and t == 1 and s < 35)):
        stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
        table[i][t][w][s][r1][r2][r3][b1][b2] = 0

    elif (i == 11 and t == 1 and w == 3 and s == 35):
        stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
        table[i][t][w][s][r1][r2][r3][b1][b2] = 0
    elif s >= 65: # 先攻のコールド勝ち
        stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
        table[i][t][w][s][r1][r2][r3][b1][b2] = 1
    elif s <= 5: # 後攻のコールド勝ち
        stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
        table[i][t][w][s][r1][r2][r3][b1][b2] = 0
    # ここまで吸収状態

    # ランナーなし   盗塁、犠打なし  凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 == 9 and r2 == 0 and r3 == 0:
        if t == 0:
            if w < 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                table[i][t][w][s][r1][r2][r3][b1][b2] = omote[b1][0] * calc(i, t, w + 1, s, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s, b1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 1, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 0, 0, b1 + 1, b2, omote, ura)
            else:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
        else: # if t!=0
            if w < 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                table[i][t][w][s][r1][r2][r3][b1][b2] = ura[b2][0] * calc(i, t, w + 1, s, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s, b2, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 1, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s, b2, 0, 0, b1, b2 + 1, omote, ura)
            else:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)

    # ランナー一塁   凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 != 9 and r2 == 0 and r3 == 0:
        if t == 0:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (omote[b1][0] - omote[b1][8]) * calc(i, t, w + 1, s, r1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][8] * calc(i, t, w + 2, s, 9, 0, 0, b1 + 1, b2, omote, ura)

                b = omote[b1][6] * calc(i, t, w, s, 9, 1, 0, b1, b2, omote, ura) + (1.0 - omote[b1][6])*calc(i, t, w + 1, s, 9, 0, 0, b1, b2, omote, ura)

                c = omote[b1][7] * calc(i, t, w + 1, s, 9, 1, 0, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7])*calc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2, omote, ura)

                d = omote[b1][0]  * calc(i, t, w + 1, s, r1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 1, 0, b1 + 1, b2, omote, ura)

                if (w == 0) or (w == 1):
                    if a == max(a, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    elif b == max(a, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = max(a, b, c)
                else:
                    if b == max(b, d): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = max(d, b)
        else:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (ura[b2][0] - ura[b2][8]) * calc(i, t, w + 1, s, r1, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s, b2, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][8] * calc(i, t, w + 2, s, 9, 0, 0, b1, b2 + 1, omote, ura)

                b = ura[b2][6] * calc(i, t, w, s, 9, 1, 0, b1, b2, omote, ura) + (1.0 - ura[b2][6]) * calc(i, t, w + 1, s, 9, 0, 0, b1, b2, omote, ura)

                c = ura[b2][7] * calc(i, t, w + 1, s, 9, 1, 0, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7]) *calc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1, omote, ura)

                d = ura[b2][0] * calc(i, t, w + 1, s, r1, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s, b2, 1, 0, b1, b2 + 1, omote, ura)

                if w == 0 or w == 1:
                    if a == min(a, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    elif b == min(a, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = min(a, b, c)
                else:
                    if b == min(d, b): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  min(d, b)

    #ランナー2塁    盗塁なし    凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 == 9 and r2 == 1 and r3 == 0:
        if t == 0:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = omote[b1][0] * calc(i, t, w + 1, s, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 1, 0, b1 + 1, b2, omote, ura)
                c = omote[b1][7] * calc(i, t, w + 1, s, 9, 0, 1, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7]) * calc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2, omote, ura)
                if w == 0 or w == 1:
                    if c == max(a, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = max(a, c)
                else:
                    stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = a
        else:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = ura[b2][0] * calc(i, t, w + 1, s, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s, b2, 1, 0, b1, b2 + 1, omote, ura)
                c = ura[b2][7] * calc(i, t, w + 1, s, 9, 0, 1, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7]) * calc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1, omote, ura)
                    
                if w == 0 or w == 1:
                    if c == min(a, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = min(a, c)
                else:
                    stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = a

    #ランナー3塁   盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 == 9 and r2 == 0 and r3 == 1:
        if t == 0:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = omote[b1][0] * calc(i, t, w + 1, s, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 0, 1, b1 + 1, b2, omote, ura)
                c = omote[b1][7] * calc(i, t, w + 1, s + 1, 9, 0, 0, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7])*calc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2, omote, ura)

                if w == 0 or w == 1:
                    if c == max(a, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = max(a, c)
                else:
                    stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = a
        else:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = ura[b2][0] * calc(i, t, w + 1, s, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s, b2, 0, 1, b1, b2 + 1, omote, ura)
                c = ura[b2][7] * calc(i, t, w + 1, s - 1, 9, 0, 0, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7])*calc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1, omote, ura)
                
                if w == 0 or w == 1:
                    if c == min(a, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = min(a, c)
                else:
                    stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = a

    #ランナー1,2塁  盗塁なし 凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 != 9 and r2 == 1 and r3 == 0:
        if t == 0:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (omote[b1][0]-omote[b1][8]) * calc(i, t, w + 1, s, r1, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][8] * calc(i, t, w + 2, s, 9, 0, 1, b1 + 1, b2, omote, ura)
                c = omote[b1][7] * calc(i, t, w + 1, s, 9, 1, 1, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7])*calc(i, t, w + 1, s, b1, 1, 0, b1 + 1, b2, omote, ura)
                d = omote[b1][0] * calc(i, t, w + 1, s, r1, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura)
                if w == 0 or w == 1:
                    if c == max(a, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, c)
                else:
                    stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = d
        else:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (ura[b2][0]-ura[b2][8]) * calc(i, t, w + 1, s, r1, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][8] * calc(i, t, w + 2, s, 9, 0, 1, b1, b2 + 1, omote, ura)
                c = ura[b2][7] * calc(i, t, w + 1, s, 9, 1, 1, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7])*calc(i, t, w + 1, s, b2, 1, 0, b1, b2 + 1, omote, ura)
                d = ura[b2][0] * calc(i, t, w + 1, s, r1, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura)

                if w == 0 or w == 1:
                    if c == min(a, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, c)
                else:
                    stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = d

    #ランナー2,3塁  盗塁なし 凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 == 9 and r2 == 1 and r3 == 1:
        if t == 0:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = omote[b1][0] * calc(i, t, w + 1, s, 9, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s + 2, b1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura)
                c = omote[b1][7] * calc(i, t, w + 1, s + 1, 9, 0, 1, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7])*calc(i, t, w + 1, s, b1, 0, 1, b1 + 1, b2, omote, ura)

                if w == 0 or w == 1:
                    if c ==  max(a, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, c)
                else:
                    stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = a
        else:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = ura[b2][0] * calc(i, t, w + 1, s, 9, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s - 2, b2, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura)
                c = ura[b2][7] * calc(i, t, w + 1, s - 1, 9, 0, 1, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7]) * calc(i, t, w + 1, s, b2, 0, 1, b1, b2 + 1, omote, ura)

                if w == 0 or w == 1:
                    if c ==  min(a, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, c)
                else:
                    stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = a

    #ランナー1,3塁  凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 != 9 and r2 == 0 and r3 == 1:
        if t == 0:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (omote[b1][0]-omote[b1][8]) * calc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][8] * calc(i, t, w + 2, s+1, 9, 0, 0, b1 + 1, b2, omote, ura)
                b = omote[b1][6] * calc(i, t, w, s, 9, 1, 1, b1, b2, omote, ura) + (1 - omote[b1][6]) * calc(i, t, w + 1, s, 9, 0, 1, b1, b2, omote, ura)
                c = omote[b1][7] * calc(i, t, w + 1, s + 1, 9, 1, 0, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7]) * calc(i, t, w + 1, s, b1, 1, 0, b1 + 1, b2, omote, ura)
                d = omote[b1][0] * calc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura)
                f = (omote[b1][0] - omote[b1][8]) * calc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][8] * calc(i, t, w + 2, s, 9, 0, 0, b1 + 1, b2, omote, ura)
                if w == 0:
                    if a ==  max(a, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    elif b ==  max(a, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, b, c)
                elif w == 1:
                    if f ==  max(f, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    elif b == max(f, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  max(f, b, c)
                else:
                    if b ==  max(b, d): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  max(b, d)
        else:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (ura[b2][0]-ura[b2][8]) * calc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1, omote, ura)  + ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][8] * calc(i, t, w + 2, s-1, 9, 0, 0, b1, b2 + 1, omote, ura)
                b = ura[b2][6] * calc(i, t, w, s, 9, 1, 1, b1, b2, omote, ura) + (1 - ura[b2][6])*calc(i, t, w + 1, s, 9, 0, 1, b1, b2, omote, ura)
                c = ura[b2][7] * calc(i, t, w + 1, s - 1, 9, 1, 0, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7])*calc(i, t, w + 1, s, b2, 1, 0, b1, b2 + 1, omote, ura)
                d = ura[b2][0] * calc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura)
                f = (ura[b2][0]-ura[b2][8]) * calc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote,ura) + ura[b2][5] * calc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][8] * calc(i, t, w + 2, s, 9, 0, 0, b1, b2 + 1, omote, ura)
                if w == 0:
                    if a ==  min(a, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    elif b ==  min(a, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, b, c)
                elif w == 1:
                    if f == min(f, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    elif b == min(f, b, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  min(f, b, c)
                else:
                    if b == min(b, d): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'S'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  min(b, d)

    #ランナー満塁   盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 != 9 and r2 == 1 and r3 == 1:
        if t == 0:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (omote[b1][0]-omote[b1][8]) * calc(i, t, w + 1, s, r1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s + 2, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 3, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 3, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 4, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s + 1, b1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][8] * calc(i, t, w + 2, s, 9, 1, 1, b1 + 1, b2, omote, ura)
                c = omote[b1][7] * calc(i, t, w + 1, s + 1, 9, 1, 1, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7])*calc(i, t, w + 1, s, b1, 1, 1, b1 + 1, b2, omote, ura)
                d = omote[b1][0] * calc(i, t, w + 1, s, r1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * calc(i, t, w, s + 2, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * calc(i, t, w, s + 3, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * calc(i, t, w, s + 3, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * calc(i, t, w, s + 4, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * calc(i, t, w, s + 1, b1, 1, 1, b1 + 1, b2, omote, ura)

                if w == 0 or w == 1:
                    if c ==  max(a, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, c)
                else:
                    stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = d
        else:
            if w == 3:
                stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
                table[i][t][w][s][r1][r2][r3][b1][b2] = calc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (ura[b2][0]-ura[b2][8]) * calc(i, t, w + 1, s, r1, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s - 2, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 3, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 3, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 4, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s - 1, b2, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][8] * calc(i, t, w + 2, s, 9, 1, 1, b1, b2 + 1, omote, ura)
                c = ura[b2][7] * calc(i, t, w + 1, s - 1, 9, 1, 1, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7])*calc(i, t, w + 1, s, b2, 1, 1, b1, b2 + 1, omote, ura)
                d = ura[b2][0] * calc(i, t, w + 1, s, r1, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * calc(i, t, w, s - 2, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * calc(i, t, w, s - 3, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * calc(i, t, w, s - 3, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * calc(i, t, w, s - 4, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * calc(i, t, w, s - 1, b2, 1, 1, b1, b2 + 1, omote, ura)
                if w == 0 or w == 1:
                    if c ==  min(a, c): stable[i][t][w][s][r1][r2][r3][b1][b2] = 'B'
                    else: stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, c)
                else:
                    stable[i][t][w][s][r1][r2][r3][b1][b2] = 'H'
                    table[i][t][w][s][r1][r2][r3][b1][b2] = d
              
    else:
        stable[i][t][w][s][r1][r2][r3][b1][b2] = 'N'
        table[i][t][w][s][r1][r2][r3][b1][b2] = 0

    return table[i][t][w][s][r1][r2][r3][b1][b2]
              

# --------------------------------------------------------------------------------------
#後攻チームの勝率を計算
def bcalc(i, t, w, s, r1, r2, r3, b1, b2, omote, ura):
    b1 = b1 % 9
    b2 = b2 % 9
    t = t % 2
    if w > 3: w = 3
    #a, b, c,d, e,f   /*a:打撃,b:盗塁,c:犠打,e:敬遠したときの勝率*/

    #printf("%d,%d,%d,%d,%d,%d,%d,%d,%d: %f\n", i, t, w, s, r1, r2, r3, b1, b2, table[i][t][w][s][r1][r2][r3][b1][b2]) */


    if btable[i][t][w][s][r1][r2][r3][b1][b2] != UNCHECK:
        return btable[i][t][w][s][r1][r2][r3][b1][b2]

    elif i >= 8 and t == 1 and w == 3 and s > 35:
        btable[i][t][w][s][r1][r2][r3][b1][b2] = 0

    elif ((i == 8 and t == 0 and w == 3 and s < 35) or (i >= 8 and t == 1 and s < 35)):
        btable[i][t][w][s][r1][r2][r3][b1][b2] = 1

    elif i == 11 and t == 1 and w == 3 and s == 35:
        btable[i][t][w][s][r1][r2][r3][b1][b2] = 0

    elif s >= 65:
        btable[i][t][w][s][r1][r2][r3][b1][b2] = 0

    elif s <= 5:
        btable[i][t][w][s][r1][r2][r3][b1][b2] = 1      #ここまで吸収状態

    #ランナーなし   盗塁、犠打なし  凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 == 9 and r2 == 0 and r3 == 0:
        if t == 0:
            if w < 3:
                btable[i][t][w][s][r1][r2][r3][b1][b2] = omote[b1][0] * bcalc(i, t, w + 1, s, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s, b1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 1, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 0, 0, b1 + 1, b2, omote, ura)
            else:
                btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
        else:
            if w < 3:
                btable[i][t][w][s][r1][r2][r3][b1][b2] = ura[b2][0] * bcalc(i, t, w + 1, s, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s, b2, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 1, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 0, 0, b1, b2 + 1, omote, ura)
            else:
                btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)

    #ランナー一塁   凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 != 9 and r2 == 0 and r3 == 0:
        if t == 0:
            if w == 3:
                btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (omote[b1][0]-omote[b1][8]) * bcalc(i, t, w + 1, s, r1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][8] * bcalc(i, t, w + 2, s, 9, 0, 0, b1 + 1, b2, omote, ura)

                b = omote[b1][6] * bcalc(i, t, w, s, 9, 1, 0, b1, b2, omote, ura) + (1.0 - omote[b1][6]) * bcalc(i, t, w + 1, s, 9, 0, 0, b1, b2, omote, ura)

                c = omote[b1][7] * bcalc(i, t, w + 1, s, 9, 1, 0, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7])*bcalc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2, omote, ura)

                d = omote[b1][0] * bcalc(i, t, w + 1, s, r1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 0, b1 + 1, b2, omote, ura)

                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, b, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  min(b, d)
    
        else:
            if w == 3:
                btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (ura[b2][0]-ura[b2][8]) * bcalc(i, t, w + 1, s, r1, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][8] * bcalc(i, t, w + 2, s, 9, 0, 0, b1, b2 + 1, omote, ura)

                b = ura[b2][6] * bcalc(i, t, w, s, 9, 1, 0, b1, b2, omote, ura) + (1.0 - ura[b2][6]) * bcalc(i, t, w + 1, s, 9, 0, 0, b1, b2, omote, ura)

                c = ura[b2][7] * bcalc(i, t, w + 1, s, 9, 1, 0, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7]) * bcalc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1, omote, ura)

                d = ura[b2][0] * bcalc(i, t, w + 1, s, r1, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 0, b1, b2 + 1, omote, ura)

                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, b, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  max(b, d)

    #ランナー2塁    盗塁なし    凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 == 9 and r2 == 1 and r3 == 0:
        if t == 0:
            if w == 3:
               btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = omote[b1][0] * bcalc(i, t, w + 1, s, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 0, b1 + 1, b2, omote, ura)
                c = omote[b1][7] * bcalc(i, t, w + 1, s, 9, 0, 1, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7]) * bcalc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2, omote, ura)

                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] = a
		
        else:
            if w == 3:
               btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = ura[b2][0] * bcalc(i, t, w + 1, s, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 0, b1, b2 + 1, omote, ura)
                c = ura[b2][7] * bcalc(i, t, w + 1, s, 9, 0, 1, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7]) * bcalc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1, omote, ura)

                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] = a

    #ランナー3塁   盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順*/
    elif r1 == 9 and r2 == 0 and r3 == 1:
        if t == 0:
            if w == 3:
              btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = omote[b1][0] * bcalc(i, t, w + 1, s, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 1, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 1, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 2, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 0, 1, b1 + 1, b2, omote, ura)
                c = omote[b1][7] * bcalc(i, t, w + 1, s + 1, 9, 0, 0, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7]) * bcalc(i, t, w + 1, s, b1, 0, 0, b1 + 1, b2, omote, ura)

                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] = a
		
        else:
            if w == 3:
              btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = ura[b2][0] * bcalc(i, t, w + 1, s, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 1, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 1, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 2, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 0, 1, b1, b2 + 1, omote, ura)
                c = ura[b2][7] * bcalc(i, t, w + 1, s - 1, 9, 0, 0, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7]) * bcalc(i, t, w + 1, s, b2, 0, 0, b1, b2 + 1, omote, ura)

                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] = a

    #ランナー1,2塁   盗塁なし  凡退、単打、二塁打、三塁打、本塁打、四球の順
    elif r1 != 9 and r2 == 1 and r3 == 0:
        if t == 0:
            if w == 3:
               btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (omote[b1][0]-omote[b1][8]) * bcalc(i, t, w + 1, s, r1, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][8] * bcalc(i, t, w + 2, s, 9, 0, 1, b1 + 1, b2, omote, ura)
                c = omote[b1][7] * bcalc(i, t, w + 1, s, 9, 1, 1, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7]) * bcalc(i, t, w + 1, s, b1, 1, 0, b1 + 1, b2, omote, ura)
                d = omote[b1][0] * bcalc(i, t, w + 1, s, r1, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura)
                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] = d
        
        else:
            if w == 3:
               btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (ura[b2][0]-ura[b2][8]) * bcalc(i, t, w + 1, s, r1, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][8] * bcalc(i, t, w + 2, s, 9, 0, 1, b1, b2 + 1, omote, ura)
                c = ura[b2][7] * bcalc(i, t, w + 1, s, 9, 1, 1, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7]) * bcalc(i, t, w + 1, s, b2, 1, 0, b1, b2 + 1, omote, ura)
                d = ura[b2][0] * bcalc(i, t, w + 1, s, r1, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura)
                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] = d

    #ランナー2,3塁    盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順   併殺打はどうするか？*/
    elif r1 == 9 and r2 == 1 and r3 == 1:
        if t == 0:
            if w == 3:
              btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = omote[b1][0] * bcalc(i, t, w + 1, s, 9, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s + 2, b1, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura)
                c = omote[b1][7] * bcalc(i, t, w + 1, s + 1, 9, 0, 1, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7]) * bcalc(i, t, w + 1, s, b1, 0, 1, b1 + 1, b2, omote, ura)

                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] = a
		
        else:
            if w == 3:
              btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = ura[b2][0] * bcalc(i, t, w + 1, s, 9, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s - 2, b2, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura)
                c = ura[b2][7] * bcalc(i, t, w + 1, s - 1, 9, 0, 1, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7])* bcalc(i, t, w + 1, s, b2, 0, 1, b1, b2 + 1, omote, ura)

                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] = a

    #ランナー1,3塁  凡退、併殺打、単打、二塁打、三塁打、本塁打、四球の順*/
    elif r1 != 9 and r2 == 0 and r3 == 1:
        if t == 0:
            if w == 3:
              btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (omote[b1][0]-omote[b1][8]) * bcalc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][8] * bcalc(i, t, w + 2, s+1, 9, 0, 0, b1 + 1, b2, omote, ura)
                b = omote[b1][6] * bcalc(i, t, w, s, 9, 1, 1, b1, b2, omote, ura) + (1 - omote[b1][6]) * bcalc(i, t, w + 1, s, 9, 0, 1, b1, b2, omote, ura)
                c = omote[b1][7] * bcalc(i, t, w + 1, s + 1, 9, 1, 0, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7]) * bcalc(i, t, w + 1, s, b1, 1, 0, b1 + 1, b2, omote, ura)
                d = omote[b1][0] * bcalc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura)
                f = (omote[b1][0] - omote[b1][8]) * bcalc(i, t, w + 1, s, r1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s + 1, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 2, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 2, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 3, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s, b1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][8] * bcalc(i, t, w + 2, s , 9, 0, 0, b1 + 1, b2, omote, ura)

                if w == 0:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, b, c)
                elif w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  min(f, b, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  min(b, d)
		
        else:
            if w == 3:
              btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (ura[b2][0]-ura[b2][8]) * bcalc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][8] * bcalc(i, t, w + 2, s-1, 9, 0, 0, b1, b2 + 1, omote, ura)
                b = ura[b2][6] * bcalc(i, t, w, s, 9, 1, 1, b1, b2, omote, ura) + (1 - ura[b2][6])*bcalc(i, t, w + 1, s, 9, 0, 1, b1, b2, omote, ura)
                c = ura[b2][7] * bcalc(i, t, w + 1, s - 1, 9, 1, 0, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7])*bcalc(i, t, w + 1, s, b2, 1, 0, b1, b2 + 1, omote, ura)
                d = ura[b2][0] * bcalc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura)
                f = (ura[b2][0]-ura[b2][8]) * bcalc(i, t, w + 1, s, r1, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s - 1, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 2, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 2, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 3, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s, b2, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][8] * bcalc(i, t, w + 2, s, 9, 0, 0, b1, b2 + 1, omote, ura)

                if w == 0:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, b, c)
                elif w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  max(f, b, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  max(b, d)

    #ランナー満塁   盗塁なし   凡退、単打、二塁打、三塁打、本塁打、四球の順*/
    elif r1 != 9 and r2 == 1 and r3 == 1:
        if t == 0:
            if w == 3:
              btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (omote[b1][0]-omote[b1][8]) * bcalc(i, t, w + 1, s, r1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s + 2, b1, 0, 1, b1 + 1, b2, omote,  ura) + omote[b1][2] * bcalc(i, t, w, s + 3, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 3, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 4, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s + 1, b1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][8] * bcalc(i, t, w + 2, s, 9, 1, 1, b1 + 1, b2, omote, ura)
                c = omote[b1][7] * bcalc(i, t, w + 1, s + 1, 9, 1, 1, b1 + 1, b2, omote, ura) + (1.0 - omote[b1][7])*bcalc(i, t, w + 1, s, b1, 1, 1, b1 + 1, b2, omote, ura)
                d = omote[b1][0] * bcalc(i, t, w + 1, s, r1, 1, 1, b1 + 1, b2, omote, ura) + omote[b1][1] * bcalc(i, t, w, s + 2, b1, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][2] * bcalc(i, t, w, s + 3, 9, 1, 0, b1 + 1, b2, omote, ura) + omote[b1][3] * bcalc(i, t, w, s + 3, 9, 0, 1, b1 + 1, b2, omote, ura) + omote[b1][4] * bcalc(i, t, w, s + 4, 9, 0, 0, b1 + 1, b2, omote, ura) + omote[b1][5] * bcalc(i, t, w, s + 1, b1, 1, 1, b1 + 1, b2, omote, ura)

                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  min(a, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] = d
		
        else:
            if w == 3:
              btable[i][t][w][s][r1][r2][r3][b1][b2] = bcalc(i + 1, t + 1, 0, s, 9, 0, 0, b1, b2, omote, ura)
            else:
                a = (ura[b2][0]-ura[b2][8]) * bcalc(i, t, w + 1, s, r1, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s - 2, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 3, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 3, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 4, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s - 1, b2, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][8] * bcalc(i, t, w + 2, s, 9, 1, 1, b1, b2 + 1, omote, ura)
                c = ura[b2][7] * bcalc(i, t, w + 1, s - 1, 9, 1, 1, b1, b2 + 1, omote, ura) + (1.0 - ura[b2][7]) * bcalc(i, t, w + 1, s, b2, 1, 1, b1, b2 + 1, omote, ura)
                d = ura[b2][0] * bcalc(i, t, w + 1, s, r1, 1, 1, b1, b2 + 1, omote, ura) + ura[b2][1] * bcalc(i, t, w, s - 2, b2, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][2] * bcalc(i, t, w, s - 3, 9, 1, 0, b1, b2 + 1, omote, ura) + ura[b2][3] * bcalc(i, t, w, s - 3, 9, 0, 1, b1, b2 + 1, omote, ura) + ura[b2][4] * bcalc(i, t, w, s - 4, 9, 0, 0, b1, b2 + 1, omote, ura) + ura[b2][5] * bcalc(i, t, w, s - 1, b2, 1, 1, b1, b2 + 1, omote, ura)
                if w == 0 or w == 1:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] =  max(a, c)
                else:
                    btable[i][t][w][s][r1][r2][r3][b1][b2] = d
    
    else:
        btable[i][t][w][s][r1][r2][r3][b1][b2] = 0

    return btable[i][t][w][s][r1][r2][r3][b1][b2]

if __name__ == "__main__":
    print("---------data installation---------------")
    top_df = data_generate(giants_bat_url)
    top_players = ["吉川尚輝", "坂本勇人", "丸佳浩", "岡本和真", "亀井善行", "阿部慎之助",  "ゲレーロ", "小林誠司", "菅野智之"]
    for i in range(len(top_players)):
        grade = list(top_df[top_df["選手名"] == top_players[i]].iloc[0,:])[1:]
        for j in range(len(grade)):
            omote[i][j] = grade[j]

    bottom_df = data_generate(carp_bat_url)
    bottom_players = ["西川龍馬", "菊池涼介", "バティスタ", "鈴木誠也", "會澤翼", "長野久義", "メヒア", "小園海斗", "大瀬良大地"]
    for i in range(len(bottom_players)):
        grade = list(bottom_df[bottom_df["選手名"] == bottom_players[i]].iloc[0,:])[1:]
        for j in range(len(grade)):
            ura[i][j] = grade[j]

    print("----------calculations start-------------")
    start = time.time()
    print("visitor win %:{:.3f}" .format(calc(0, 0, 0, 35, 9, 0, 0, 0, 0, omote, ura)))
    #print("home win %:{}" .format(bcalc(8, 0, 0, 33, 9, 0, 0, 0, 0, omote, ura)))
    end = time.time()
    print("calculation time:", end-start)
    print("Finish")
