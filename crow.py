from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

# WebDriver 초기화
chromedriver_url = 'C:/chromedriver-win64/chromedriver.exe'
chrome_service = Service(chromedriver_url)
chrome_options = Options()
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# 네이버 웹툰 페이지 열기
nw_url = 'https://comic.naver.com/webtoon/weekday'
driver.get(nw_url)

# 제목 요소들이 로드될 때까지 대기
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "title")))

# 페이지 로딩 상태 확인
WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

# 요소들이 로드될 때까지 대기
try:
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "title")))
except Exception as e:
    print("요소를 찾는 데 실패했습니다:", e)
    print(driver.page_source)  # 디버깅을 위해 페이지 소스 출력
    driver.quit()
    exit()

# 클릭 가능한 제목 요소 리스트 가져오기
titles = driver.find_elements(By.CLASS_NAME, "title")

# 데이터 저장을 위한 리스트 정의
id_list = []
title_list = []
author_list = []
day_list = []
genre_list = []
story_list = []
platform_list = []
webtoon_url_list = []
thumbnail_url_list = []

webtoon_id = 0

# 제목 리스트를 반복하면서 데이터 크롤링
for i in range(len(titles)):
    print(f"\r진행 상황: {i + 1} / {len(titles)}", end="")

    # 안정성을 위해 잠시 대기
    sleep(0.5)

    # 현재 타이틀 클릭
    titles = driver.find_elements(By.CLASS_NAME, "title")
    titles[i].click()

    # 이동한 페이지가 로드될 때까지 대기
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "comicinfo")))

    # 페이지 소스 가져와서 BeautifulSoup으로 파싱
    html = driver.page_source
    soup = bs(html, 'html.parser')

    # 웹툰 정보 추출
    title = soup.find('span', {'class': 'title'}).text.strip()
    day = soup.find('ul', {'class': 'category_tab'}).find('li', {'class': 'on'}).text.strip()[0:1]

    # 이미 저장된 웹툰인지 확인 (다른 요일에도 연재되는 경우)
    if title in title_list:
        day_list[title_list.index(title)] += ', ' + day
        driver.back()
        continue

    # 나머지 정보 추출
    thumbnail_url = soup.find('div', {'class': 'thumb'}).find('img')['src']
    author = soup.find('span', {'class': 'wrt_nm'}).text.strip()[8:].replace(' / ', ', ')
    genre = soup.find('span', {'class': 'genre'}).text.strip()
    story = soup.find('div', {'class': 'detail'}).find('p').text.strip()

    # 리스트에 데이터 추가
    id_list.append(webtoon_id)
    title_list.append(title)
    author_list.append(author)
    day_list.append(day)
    genre_list.append(genre)
    story_list.append(story)
    platform_list.append("네이버")
    webtoon_url_list.append(driver.current_url)
    thumbnail_url_list.append(thumbnail_url)

    # 뒤로 가기
    driver.back()
    webtoon_id += 1
    sleep(0.5)

    # 뒤로 간 후에 다시 제목 요소들 가져오기
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "title")))

input("Press Enter to close the browser...")

# 작업 완료 후 WebDriver 종료
driver.quit()
