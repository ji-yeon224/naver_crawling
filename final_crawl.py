import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time

from selenium.webdriver.common.keys import Keys

category_name=['침실가구','거실가구','서재/사무용가구','주방가구','수납가구']
href = []
bed = ['침대','매트리스','장롱/붙박이장','화장대','거울','협탁','부부테이블','침실세트','서랍장']
living = ['소파','테이블','TV거실장','장식장']
kitchen = ['식탁/의자','레인지대','왜건/카트','주방수납장','그릇장/컵보드','와인용품','기타주방가구']
storage = ['행거','수납장','선반','공간박스','고가구','나비장','CD/DVD장','신발장','우산꽂이','잡지꽂이','코너장','소품수납함']
library = ['책상','의자','책장','책꽂이','사무/교구용가구']


for j in range(0, 9):  # 카테고리 별 상품 개수 for문임 (bed는 9개니까 0부터 9 -> item_list파일 개수대로하기)
    filename = './item_list/bed/' + "bed" + str(j) + '.csv'  # bed 폴더랑 파일 이름 만 변경하면됨
    file = open(filename, 'r', encoding='utf-8-sig')
    data = pd.read_csv(file)
    print(filename)
    links = data['pd_href']
    driver = webdriver.Chrome('./chromedriver.exe')

    for a in range(0, len(links)):  # 원하는 review파일 숫자부터~링크수까지
        print(len(links))
        # for a in links:
        print(links[a])
        driver.get(links[a])
        last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(1.0)  # 인터발 1이상으로 줘야 데이터 취득가능(롤링시 데이터 로딩 시간 때문)
            new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_page_height == last_page_height:
                break
            last_page_height = new_page_height
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, "lxml")

        result = []

        # 리뷰 다음페이지 버튼 1번 페이지가 2임  그래서 5번페이지까지 뽑음 만약 없으면 pass
        page = 2
        while page < 7:
            time.sleep(3)
            if page != 2:
                try:
                    bt = driver.find_element_by_xpath('//*[@id="REVIEW"]/div/div[3]/div/div[2]/a['+str(page)+']').send_keys(Keys.ENTER)
                except:
                    break
                time.sleep(3)
            page += 1

            # 변경된 url로  페이지 소스 가져오기
            html_source1 = driver.page_source
            soup = BeautifulSoup(html_source1, "html.parser")
            driver.implicitly_wait(30)

            stars = []
            ul = soup.find('ul', {'class': '_1iaDS5tcmC'})
            ems = ul.find_all('em')
            for em in ems:
                stars.append(em.text)
            review = soup.select("div._3AGQlpCnyu>span._2Xe0HVhCew")
            customerId = soup.select("div._2DSGiSauFJ>strong._2Xe0HVhCew")
            reviewDate = soup.select("div._2DSGiSauFJ>span._2Xe0HVhCew")

            for k in range(len(review)):
                s = stars[k]
                r = review[k].text
                c = customerId[k].text
                rD = reviewDate[k].text
                c1=bed[j]
                c2=category_name[0]
                result.append([str(k), s, r, c, rD ,c1 ,c2])
            print(len(review))
            if len(review) < 20:
                break

        if len(result) == 0:  # result(review) 하나도 없으면 다음
            continue
        else:

            print(result)

            data = pd.DataFrame(result)
            data.columns = ['review_no','star', 'review', 'customerId', 'reviewDate','pd_no','bedcate_no','category_no']

            filename = 'reviews/bed/bed' + str(j) + "-review" + str(a) + ".csv"
            # bed0-review0.csv 이런식 으로 저장
            data.to_csv(filename, encoding='utf-8-sig', index = False)

    file.close()
    driver.close()
