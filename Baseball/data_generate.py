# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import time
from bs4 import BeautifulSoup
import pandas as pd
import urllib

giants_url = "https://baseballdata.jp/1/ctop.html"
swallows_url = "https://baseballdata.jp/2/ctop.html"
dena_url = "https://baseballdata.jp/3/ctop.html"
dragons_url = "https://baseballdata.jp/4/ctop.html"
tigers_url = "https://baseballdata.jp/5/ctop.html"
carp_url = "https://baseballdata.jp/6/ctop.html"

lions_url = "https://baseballdata.jp/7/ctop.html"
fighters_url = "https://baseballdata.jp/8/ctop.html"
lotte_url = "https://baseballdata.jp/9/ctop.html"
orix_url = "https://baseballdata.jp/11/ctop.html"
hawks_url = "https://baseballdata.jp/12/ctop.html"
eagles_url = "https://baseballdata.jp/376/ctop.html"

def data_generate(URL):
    html = urllib.request.urlopen(URL)

    # htmlをBeautifulSoupで扱う
    soup = BeautifulSoup(html, "html.parser")

    tmp_data= []
    web_data = soup.tbody.findAll("tr")
    for i in range(len(web_data)):
        row_tmp = web_data[i].getText().replace("\r", "").replace(" ", "").split("\n")
        row = [a for a in row_tmp if a != '']
        if row not in tmp_data and "○" in row:
            print("{}_{}".format(row, len(row)))
            tmp_data.append(row)
        elif "選手名" in row:
            title = row
    
    title.remove("調子")
    df = pd.DataFrame(tmp_data[0])
    for i in range(1, len(tmp_data)):
        ind_data = pd.DataFrame(tmp_data[i])
        df = pd.concat([df, ind_data], axis=1)

    df = df.T
    df.columns = title
    team = df.iloc[0]["球団"]
    
    # データの型をobject型からint、またはfloat型に変換する
    for i in ["打点", "本塁打", "安打数", "単打", "2塁打", "3塁打", "得点圏打数", "得点圏安打", 
              "UC本塁打", "試合数", "打席数", "打数", "得点","四球", "死球", "企盗塁", "盗塁", 
              "企犠打","犠打", "犠飛", "代打数", "代打安打", "併殺", "失策", "三振"]:
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
    df["選手名"] = df["選手名"].apply(lambda x: x.split(":")[1].split(".")[0].split(team)[0])
    
    # 各選手について 凡退,単打率 二塁打率 三塁打率 本塁打率 四死球率 盗塁成功率 犠打成功率　併殺打率を計算する
    df["単打率"] = df["単打"] / (df["打席数"] - df["犠打"])
    df["二塁打率"] = df["2塁打"] / (df["打席数"] - df["犠打"])
    df["三塁打率"] = df["3塁打"] / (df["打席数"] - df["犠打"])
    df["本塁打率"] = df["本塁打"] / (df["打席数"] - df["犠打"])
    df["四死球率"] = (df["四球"] + df["死球"]) / (df["打席数"] - df["犠打"])
    df["併殺打率"] = df["併殺"] / (df["打席数"] - df["犠打"])
    df["凡退率"] = 1 - df["出塁率"]
    df["併殺打率"] = df["併殺"] / (df["打席数"] - df["犠打"])

    calc_df = df[["選手名", "凡退率","単打率","二塁打率","三塁打率","本塁打率","四死球率","盗塁成功率","犠打成功率", "併殺打率"]]
    return calc_df

print("###########")
print("Central League")
print("###########")

# https://stackoverflow.com/questions/31247198/python-pandas-write-content-of-dataframe-into-text-file
giants = data_generate(giants_url)
giants.iloc[:9,1:].to_csv(r'data/giants.txt', header=None, index=None, sep=' ', mode='w')
swallows = data_generate(swallows_url)
swallows.iloc[:9,1:].to_csv(r'data/swallows.txt', header=None, index=None, sep=' ', mode='w')
dena = data_generate(dena_url)
dena.iloc[:9,1:].to_csv(r'data/dena.txt', header=None, index=None, sep=' ', mode='w')
tigers = data_generate(tigers_url)
tigers.iloc[:9,1:].to_csv(r'data/tigers.txt', header=None, index=None, sep=' ', mode='w')
dragons = data_generate(dragons_url)
dragons.iloc[:9,1:].to_csv(r'data/dragons.txt', header=None, index=None, sep=' ', mode='w')
carp = data_generate(carp_url)
carp.iloc[:9,1:].to_csv(r'data/carp.txt', header=None, index=None, sep=' ', mode='w')

print("###########")
print("Pacific League")
print("###########")
lions = data_generate(lions_url)
lions.iloc[:9,1:].to_csv(r'data/lions.txt', header=None, index=None, sep=' ', mode='w')
fighters = data_generate(fighters_url)
fighters.iloc[:9,1:].to_csv(r'data/fighters.txt', header=None, index=None, sep=' ', mode='w')
eagles = data_generate(eagles_url)
eagles.iloc[:9,1:].to_csv(r'data/eagles.txt', header=None, index=None, sep=' ', mode='w')
lotte = data_generate(lotte_url)
lotte.iloc[:9,1:].to_csv(r'data/lotte.txt', header=None, index=None, sep=' ', mode='w')
orix = data_generate(orix_url)
orix.iloc[:9,1:].to_csv(r'data/orix.txt', header=None, index=None, sep=' ', mode='w')
hawks = data_generate(hawks_url)
hawks.iloc[:9,1:].to_csv(r'data/hawks.txt', header=None, index=None, sep=' ', mode='w')

print("###########")
print("FINISH")
print("###########")
