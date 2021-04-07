import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time

from selenium.webdriver.common.keys import Keys


reviewImage = []

for j in range(0, 12):  # 카테고리 별 상품 개수 for문임 (bed는 9개니까)
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
                    bt = driver.find_element_by_xpath(
                        '//*[@id="REVIEW"]/div/div[3]/div/div[2]/a[' + str(page) + ']').send_keys(Keys.ENTER)
                except:
                    break
                time.sleep(3)
            page += 1

            html_source1 = driver.page_source
            soup = BeautifulSoup(html_source1, "html.parser")
            driver.implicitly_wait(30)

            stars = []
            ul = soup.find('ul', {'class': '_1iaDS5tcmC'})
            ems = ul.find_all('em')
            for em in ems:
                stars.append(em.text)
            review = soup.select("div._3AGQlpCnyu>span._2Xe0HVhCew")
            reviewImages = soup.select('div._28mE__69Rv>span._30jCYXkysR>img:nth-of-type(1)')
            for i in reviewImages:
                reviewImage.append(i.attrs['src'])
                # print(reviewImage)

            customerId = soup.select("div._2DSGiSauFJ>strong._2Xe0HVhCew")
            # option = soup.select("div._31mfFx_-xd>button.NIYM68WJ2v>span._2Xe0HVhCew")
            reviewDate = soup.select("div._2DSGiSauFJ>span._2Xe0HVhCew")

            for k in range(len(review)):
                s = stars[k]
                r = review[k].text

                c = customerId[k].text
                # o = option[k].text
                rD = reviewDate[k].text

                result.append([str(k), s, r, c, rD])
            print(len(review))
            if len(review) < 20:
                break

        if len(result) == 0:  # result(review) 하나도 없으면 다음
            continue
        else:

            print(result)

            data = pd.DataFrame(result)
            data.columns = ['review_no','star', 'review', 'customerId', 'reviewDate']

            filename = 'reviews/bed/bed' + str(j) + "-review" + str(a) + ".csv"
            # bed0-review0.csv 이런식 으로 저장
            data.to_csv(filename, encoding='utf-8-sig', index = False)

    driver.close()
    file.close()


