
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import requests

url='https://search.shopping.naver.com/category/category/50000004'
driver = webdriver.Chrome('./chromedriver.exe')
driver.implicitly_wait(30)
driver.get(url)

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
    hrefs[i]='https://search.shopping.naver.com'+hrefs[i]+'&productSet=window&pagingSize=10'

hrefs[4] = hrefs[5]
hrefs[5]=None



#링크 들어가서 중간 카테고리 가져오기
i=0
category_arr=[]
driver2 = webdriver.Chrome('./chromedriver.exe')
while i<5:

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




cate = ['bed', 'living', 'kitchen', 'storage', 'library']
idx = []
for i in range(5):
    idx.append(len(category_arr[i]))





