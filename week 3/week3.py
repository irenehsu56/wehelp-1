# Task 1
import urllib.request as request
import json
import csv
ch_url="https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-ch"
en_url="https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-en"

def get_data(url):
    with request.urlopen(url) as response:
        data=response.read().decode("utf-8")
        return json.loads(data) # 利用 JSON 模組處理 JSON 資料格式

ch_data=get_data(ch_url)
en_data=get_data(en_url)

# 用 id 整理英文資料的順序
en_dict={}
for hotel in en_data["list"]:
    en_dict[hotel["_id"]]=hotel

# 建立行政區資料
districts={}

with open("hotels.csv", "w", encoding="utf-8", newline="") as file:
    writer=csv.writer(file)

    for hotel in ch_data["list"]:
        hotel_id=hotel["_id"]
        en_hotel=en_dict.get(hotel_id)

        chinese_name = hotel["旅宿名稱"]
        english_name = en_hotel["hotel name"]
        chinese_address = hotel["地址"]
        english_address = en_hotel["address"]
        phone = hotel["電話或手機號碼"]
        room_count = int(hotel["房間數"])

        writer.writerow([
            chinese_name,
            english_name,
            chinese_address,
            english_address,
            phone,
            room_count
        ])

        # 從中文地址抓行政區
        district=chinese_address.split("市")[1].split("區")[0]+"區"

        if district not in districts:
            districts[district]={
                "hotel_count":0, 
                "room_count":0
            }
        districts[district]["hotel_count"]+=1
        districts[district]["room_count"]+=room_count

with open("districts.csv", "w", encoding="utf-8", newline="") as file:
    writer=csv.writer(file)

    for district in districts:
        writer.writerow([
            district,
            districts[district]["hotel_count"],
            districts[district]["room_count"]
        ])

# Task 2
import urllib.request as request
import csv
from bs4 import BeautifulSoup

base_url="https://www.ptt.cc" # 基礎網址
start_url="https://www.ptt.cc/bbs/Steam/index.html" # 起始頁面

def get_soup(url): # 取得 BeautifulSoup 解析後的結果
    req=request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )
    with request.urlopen(req) as response: # 打開網頁
        html=response.read().decode("utf-8")

    return BeautifulSoup(html, "html.parser") # 把 HTML 交給 BeautifulSoup 解析

def get_publish_time(article_url):
    soup=get_soup(article_url)

    meta_values=soup.find_all("span", class_="article-meta-value") # 找文章上方的資訊，作者/看板/標題/時間

    if len(meta_values) >= 4:
        return meta_values[3].text.strip() # 取得發佈時間，.text 是取標籤內的文字，.strip() 是去掉前後空白和換行
    else:
        return ""

articles=[]
page_url=start_url

# 解析前 3 頁
for i in range(3):
    soup=get_soup(page_url)

    article_blocks=soup.find_all("div", class_="r-ent") # PTT 網頁裡的 class 名稱

    for block in article_blocks:
        title_tag=block.find("div", class_="title").find("a") # 找文章標題

        # 如果文章被刪除，就沒有 a 標籤，直接跳過
        if title_tag is None:
            continue

        title=title_tag.text.strip() # 抓 a 裡的文字，並去掉前後空白

        like_tag=block.find("div", class_="nrec") 
        like_count=like_tag.text.strip() # 抓文章的按讚數

        article_link=title_tag["href"] # 取文章連結
        article_url=base_url + article_link # 把主網址和文章連結合併起來

        publish_time=get_publish_time(article_url) # 進文章頁抓發布時間

        articles.append([
            title,
            like_count,
            publish_time
        ])

    # 找「上頁」連結，準備爬下一頁
    paging_links=soup.find_all("a", class_="btn wide")

    for link in paging_links:
        if link.text == "‹ 上頁":
            page_url=base_url + link["href"] # 把主網址和上頁的文章連結合併起來
            break


with open("articles.csv", "w", encoding="utf-8", newline="") as file:
    writer=csv.writer(file)

    for article in articles:
        writer.writerow(article)