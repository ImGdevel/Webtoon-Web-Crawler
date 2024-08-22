from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep

# WebDriver 초기화 (크롬 드라이버 경로 및 서비스 설정)
chromedriver_url = 'C:/chromedriver-win64/chromedriver.exe'
chrome_service = Service(chromedriver_url)
chrome_options = Options()
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# 네이버 웹툰 페이지 열기 (네이버 웹툰의 요일별 웹툰 목록 페이지)
nw_url = 'https://comic.naver.com/webtoon/weekday'
driver.get(nw_url)

# 페이지 로딩 상태 확인 (문서 로드가 완료될 때까지 대기)
WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

# 요소들이 로드될 때까지 대기 (웹툰 제목 영역이 로드될 때까지 대기)
try:
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ContentTitle__title_area")))
except Exception as e:
    print("TimeoutException: 요소를 찾지 못했습니다. 다음 작업으로 넘어갑니다.")
    # 타임아웃이 발생하더라도 프로그램이 종료되지 않고 다음 단계로 넘어갑니다.

# 클릭 가능한 제목 요소 가져오기 (웹툰 제목들을 가져옴)
titles = driver.find_elements(By.CLASS_NAME, "ContentTitle__title_area")

# 데이터를 저장할 리스트들 초기화
id_list = []
title_list = []
author_list = []
day_list = []
genre_list = []
story_list = []
platform_list = []
webtoon_url_list = []
thumbnail_url_list = []

webtoon_id = 0  # 웹툰 ID 초기화

# 제목을 순회하며 데이터 스크래핑 (모든 웹툰 제목들을 순회하며 정보를 수집)
for i in range(len(titles)):
    print(f"\rprocess: {i + 1} / {len(titles)}", end="")  # 진행 상황 출력

    # 안정성을 위해 상호작용 전 대기 (0.5초 대기)
    sleep(0.5)

    # 제목 요소들을 다시 가져와서 현재 항목 클릭 (페이지가 로드되었는지 확인하고, 웹툰 제목을 클릭)
    titles = driver.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
    titles[i].click()

    # 페이지 로드 대기 (필수 요소가 로드될 때까지 대기)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ContentTitle__title_area--x24vt")))
    except Exception as e:
        print("TimeoutException: 웹툰 페이지 로드 중 오류가 발생했습니다. 다음 작업으로 넘어갑니다.")
        driver.back()  # 타임아웃 발생 시 뒤로 가기
        continue

    # 페이지 소스 가져오기 및 BeautifulSoup으로 파싱 (HTML 코드를 가져와서 파싱)
    html = driver.page_source
    soup = bs(html, 'html.parser')

    # 정보 추출 (웹툰 제목 추출)
    title = soup.find('span', {'class': 'EpisodeListInfo__title--mYLjC'}).text.strip()

    # 요일 정보 추출 (현재 탭에 선택된 요일 추출)
    day = soup.find('ul', {'class': 'category_tab'}).find('li', {'class': 'on'}).text.strip()[0:1]

    # 제목이 이미 존재하는지 확인 (여러 요일에 중복되는 경우 처리)
    if title in title_list:
        day_list[title_list.index(title)] += ', ' + day
        driver.back()
        continue

    # 기타 정보 추출 (썸네일, 작가, 장르, 줄거리 등)
    thumbnail_url = soup.find('div', {'class': 'thumb'}).find('img')['src']
    author = soup.find('span', {'class': 'wrt_nm'}).text.strip()[8:].replace(' / ', ', ')
    genre = soup.find('span', {'class': 'genre'}).text.strip()
    story = soup.find('div', {'class': 'detail'}).find('p').text.strip()

    # 데이터 리스트에 추가 (추출된 정보를 리스트에 저장)
    id_list.append(webtoon_id)
    title_list.append(title)
    author_list.append(author)
    day_list.append(day)
    genre_list.append(genre)
    story_list.append(story)
    platform_list.append("네이버")
    webtoon_url_list.append(driver.current_url)
    thumbnail_url_list.append(thumbnail_url)

    # 뒤로 가기 및 웹툰 ID 증가 (수집이 끝난 후 이전 페이지로 돌아가고 ID를 증가시킴)
    driver.back()
    webtoon_id += 1
    sleep(0.5)

# 작업이 끝나면 브라우저 닫기 (브라우저를 종료)
input("Press Enter to close the browser...")
driver.quit()
