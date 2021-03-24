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
import crawl as c

from selenium.webdriver.common.keys import Keys

#큰 카테고리 링크 들어가기
for i in range(len(c.hrefs)):
    print("@@")
    driver = webdriver.Chrome('./chromedriver.exe')
    url = c.hrefs[i]
    driver.get(url)
    cate = c.cate[i] #파일이름에 붙일 카테고리 이름

    # 중간카테고리 클릭
    for j in range(c.idx[i]):
        print("##")
        link = driver.find_element_by_xpath(
            '//*[@id="__next"]/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div/ul/li['+str(j+1)+']/a')
        link.send_keys(Keys.ENTER)
        time.sleep(3)

        mid_url = driver.current_url
        page = 1
        idx = 0 #파일 이름에 붙일 숫자
        idx+=1
        str_list = [] # 상품목록배열
        # 80개씩 2페이지, 최대 160개 리스트 가져오기
        while page < 3:

            if page == 2: # 다음 페이지에서 80개 가져오기
                print(page)
                link = driver.find_element_by_xpath(
                    '//*[@id="__next"]/div/div[2]/div/div[3]/div[1]/div[3]/div/a[1]').send_keys(Keys.ENTER)
            time.sleep(3)
            page += 1

            #스크롤 내리기
            last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(1.0)  # 인터발 1이상으로 줘야 데이터 취득가능(롤링시 데이터 로딩 시간 때문)
                new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_page_height == last_page_height:
                    break
                last_page_height = new_page_height
            # 변경된 url로  페이지 소스 가져오기
            html_source1 = driver.page_source
            soup = BeautifulSoup(html_source1, "html.parser")
            driver.implicitly_wait(30)

            # 상품목록 각 요소들 크롤링
            title = soup.select("div.basicList_title__3P9Q7")

            myelements = soup.select(
                '#__next > div > div.style_container__1YjHN > div > div.style_content_wrap__1PzEo > div.style_content__2T20F > ul > div > div')

            href = [div.find("a")['href'] for div in myelements]
            page_item_num = len(href) #한페이지에 상품 몇개 있는지 확인용
            img = []
            exp_idx = [] #판매불가 링크 인덱스 보관용
            #상품링크로 들어가기
            for i in range(len(href)):
                driver.get(href[i])
                try:
                    images = driver.find_element_by_xpath("//*[@id='content']/div[2]/div[1]/div[1]/div[1]/img")
                    img.append(images.get_attribute('src'))
                except: #판매불가 링크는 인덱스만 보관하고 넘어가기
                    exp_idx.append(i)
                    pass

            # print(img)

            price = soup.select("div.basicList_price_area__1UXXR")
            # cate2 = soup1.select("div.basicList_depth__2QIie>a:nth-of-type(2)")
            # cate3 = soup1.select("div.basicList_depth__2QIie>a:nth-of-type(3)")
            # mallName = soup1.select("div.basicList_mall_title__3MWFY>a")

            #판매불가 상품 정보 제외시키기
            for e in range(len(exp_idx)):
                del href[exp_idx[e]]
                del title[exp_idx[e]]
                del price[exp_idx[e]]
                #del cate2[e]
                #del cate3[e]
                #del mallName[e]


            for j in range(len(price)):
                t = title[j].text
                h = href[j]
                i = img[j]
                p = price[j].text
                # c2 = cate2[j].text
                # c3 = cate3[j].text
                # m = mallName[j].text
                str_list.append([t, h, i, p])
            print(str_list)

            # 한 페이지에 있는 개수가 80개보다 적으면 이동할 페이지 없음 -> 반복문 종료
            if page_item_num < 80:
                break
            else: #페이지 넘기기위해 상품 목록화면으로 다시 넘어가기
                driver.get(mid_url)

        # 상품리스트 csv파일만들기
        data = pd.DataFrame(str_list)
        data.columns = ['pd_title', 'pd_href', 'pd_img', 'pd_price']
        filename = cate + str(idx) + ".csv"
        data.to_csv(filename, encoding='utf-8-sig')

        driver.get(url)




    # print(str_list)



driver.close()