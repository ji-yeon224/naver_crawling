import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import requests
from urllib.parse import urlparse
from urllib.parse import quote
import json
import urllib.request
import re



start = time.time()
driver = webdriver.Chrome('chromedriver')
url='https://search.shopping.naver.com/category/category/50000004'
driver = webdriver.Chrome('./chromedriver.exe')
driver.implicitly_wait(30)
driver.get(url)
last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(1.0)       # 인터발 1이상으로 줘야 데이터 취득가능(롤링시 데이터 로딩 시간 때문)
    new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_page_height == last_page_height:
        break
    last_page_height = new_page_height
html_source = driver.page_source

soup = BeautifulSoup(html_source, "lxml")
bigcategory= soup.select("div.__50000004_category_cell__yNbrS > h3 > a > strong")
str_bigcategory = []
for i in range(6):
    str_tmp = str(bigcategory[i].text)
    str_tmp = str_tmp.replace('\n', '')
    str_tmp = str_tmp.replace('\t', '')
    str_tmp = str_tmp.replace('   ', '')
    str_bigcategory.append(str_tmp)

str_bigcategory[4]=str_bigcategory[5]
str_bigcategory[5]=None
#for i in range(6):
#    print(str_bigcategory[i])

result = requests.get(url)
bs_obj = BeautifulSoup(result.content, "html.parser")

#각 카테고리 링크 추출 (침실가구, 주방가구 어쩌구,,)
link = bs_obj.findAll("div", {"class":"__50000004_category_cell__yNbrS"})
hrefs = [div.find("a")['href'] for div in link]
for i in range(6):
    hrefs[i]='https://search.shopping.naver.com'+hrefs[i]
hrefs[4] = hrefs[5]
hrefs[5]=None


#링크 들어가서 중간 카테고리 가져오기
i=0
category_arr=[]
while i<5:
    driver2 = webdriver.Chrome('./chromedriver.exe')
    driver2.get(hrefs[i])
    html_source1 = driver2.page_source
    soup1 = BeautifulSoup(html_source1, "lxml")
    time.sleep(1.0)
    category = soup1.select(
        "#__next > div > div.style_container__1YjHN > div > div.filter_finder__1Gtei > div.filter_finder_filter__1DTIN > div.filter_finder_col__3ttPW.filter_is_active__3qqoC > div.filter_finder_row__1rXWv > div > ul > li > a > span")
    str_category = []
    for j in range(len(category)):
        str_tmp = str(category[j].text)
        str_tmp = str_tmp.replace('\n', '')
        str_tmp = str_tmp.replace('\t', '')
        str_tmp = str_tmp.replace('   ', '')
        str_category.append(str_tmp)
    category_arr.append(str_category)
    driver.get(url)
    time.sleep(1.0)
    i+=1
    driver2.close()

driver.close()


#각 카테고리별로 네이버 검색하여 추출
def craw_item(filename, category):
    client_id = "BHheLl5ZCosrew_YXt3H"
    client_secret = "Tv_QBQDLmk"
    encText = urllib.parse.quote(category)
    url = "https://openapi.naver.com/v1/search/shop.json?query=" + encText + "&display=100"  # json 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
    else:
        print("Error Code:" + rescode)

    #print("**")
    text_data = response_body.decode('utf-8')
    json_data = json.loads(text_data)
    result = []
    for x in json_data['items']:
        title = re.sub('<.+?>', '', x['title'], 0, re.I | re.S)
        link = x['link']
        image = x['image']
        price = x['lprice']
        cate2 = x['category2']
        cate3 = x['category3']
        mallName = x['mallName']
        result.append([title, price, cate2, cate3, mallName, link, image])
    #print(result)

    #csv파일에 저장
    data = pd.DataFrame(result)
    data.columns = ['title', 'price', 'cate1_no', 'cate2_no', 'mallName', 'link', 'image']
    data.to_csv(filename, encoding='utf-8-sig')


cate = ['bed', 'living', 'kitchen', 'storage', 'library']
for i in range(5):
    for j in range(len(category_arr[i])):
        filename = cate[i]+str(j)+".csv"
        craw_item(filename, category_arr[i][j])




