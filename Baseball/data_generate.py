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
softbank_url = "https://baseballdata.jp/12/ctop.html"
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
    df["2塁打率"] = df["2塁打"] / (df["打席数"] - df["犠打"])
    df["3塁打率"] = df["3塁打"] / (df["打席数"] - df["犠打"])
    df["本塁打率"] = df["本塁打"] / (df["打席数"] - df["犠打"])
    df["四死球率"] = (df["四球"] + df["死球"]) / (df["打席数"] - df["犠打"])
    df["併殺打率"] = df["併殺"] / (df["打席数"] - df["犠打"])
    df["凡退率"] = 1 - df["出塁率"]

    return df

print("###########")
print("Central League")
print("###########")

giants = data_generate(giants_url)
giants.to_csv("data/giants.csv")
swallows = data_generate(swallows_url)
swallows.to_csv("data/swallows.csv")
dena = data_generate(dena_url)
dena.to_csv("data/dena.csv")
tigers = data_generate(tigers_url)
tigers.to_csv("data/tigers.csv")
dragons = data_generate(dragons_url)
dragons.to_csv("data/dragons.csv")
carp = data_generate(carp_url)
carp.to_csv("data/carp.csv")

print("###########")
print("Pacific League")
print("###########")
lions = data_generate(lions_url)
lions.to_csv("data/lions.csv")
fighters = data_generate(fighters_url)
fighters.to_csv("data/fighters.csv")
eagles = data_generate(eagles_url)
eagles.to_csv("data/eagles.csv")
lotte = data_generate(lotte_url)
lotte.to_csv("data/lotte.csv")
orix = data_generate(orix_url)
orix.to_csv("data/orix.csv")
hawks = data_generate(hawks_url)
hawks.to_csv("data/hawks.csv")
