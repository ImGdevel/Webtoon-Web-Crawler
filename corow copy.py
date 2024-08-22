import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep
from typing import List, Dict
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import json

# 전역 상수로 HTML 클래스 이름을 설정하여 직관적인 변수명 사용
NAVER_WEBTOON_URLS = [
    'https://comic.naver.com/webtoon?tab=mon',
    'https://comic.naver.com/webtoon?tab=tue',
    'https://comic.naver.com/webtoon?tab=wed',
    'https://comic.naver.com/webtoon?tab=thu',
    'https://comic.naver.com/webtoon?tab=fri',
    'https://comic.naver.com/webtoon?tab=sat',
    'https://comic.naver.com/webtoon?tab=sun',
    'https://comic.naver.com/webtoon?tab=dailyPlus',
    'https://comic.naver.com/webtoon?tab=finish'
]
CHROMEDRIVER_PATH = 'C:/chromedriver-win64/chromedriver.exe'
CONTENT_LIST_CLASS = "ContentList__content_list--q5KXY"
ITEM_CLASS = "item"
RATING_CLASS = "Rating__star_area--dFzsb"
TITLE_AREA_CLASS = "ContentTitle__title_area--x24vt"

class WebDriverFactory:
    @staticmethod
    def create_chrome_driver(chromedriver_path: str) -> webdriver.Chrome:
        chrome_service = Service(chromedriver_path)
        chrome_options = Options()
        return webdriver.Chrome(service=chrome_service, options=chrome_options)

class WebtoonScraper:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def open_page(self, url: str):
        self.driver.get(url)
        WebDriverWait(self.driver, 3).until(lambda d: d.execute_script('return document.readyState') == 'complete')

    def get_webtoon_elements(self) -> List[webdriver.remote.webelement.WebElement]:
        return WebDriverWait(self.driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, ITEM_CLASS))
        )

    def scrape_webtoon_info(self, webtoon_element) -> Dict[str, str]:
        try:
            # 평점 추출
            rating = webtoon_element.find_element(By.CLASS_NAME, RATING_CLASS).text.strip()

            # 링크 추출 및 이동
            title_element = webtoon_element.find_element(By.CLASS_NAME, TITLE_AREA_CLASS)
            title_element.click()

            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, TITLE_AREA_CLASS)))
            soup = bs(self.driver.page_source, 'html.parser')

            title = soup.find('h2', {'class': 'EpisodeListInfo__title--mYLjC'}).text.strip()
            day = soup.find('div', {'class': 'ContentMetaInfo__meta_info--GbTg4'}).find('em', {'class': 'ContentMetaInfo__info_item--utGrf'}).text.strip()
            thumbnail_url = soup.find('div', {'class': 'Poster__thumbnail_area--gviWY'}).find('img')['src']
            #author = soup.find('span', {'class': 'wrt_nm'}).text.strip()[8:].replace(' / ', ', ')
            #genre = soup.find('span', {'class': 'genre'}).text.strip()
            story = soup.find('div', {'class': 'EpisodeListInfo__summary_wrap--ZWNW5'}).find('p').text.strip()

            return {
                "title": title,
                "day": day,
                "rating": rating,
                "thumbnail_url": thumbnail_url,
                #"author": author,
                #"genre": genre,
                "story": story,
                "url": self.driver.current_url
            }
        except TimeoutException:
            print("TimeoutException: Could not load webtoon page. Skipping...")
            return None
        finally:
            self.driver.back()
            sleep(0.1)

class WebtoonRepository:
    def __init__(self):
        self.webtoons = []
        self.webtoon_id = 0

    def save(self, webtoon_data: Dict[str, str]):
        if self._exists(webtoon_data["title"]):
            self._update_day(webtoon_data)
        else:
            webtoon_data["id"] = self.webtoon_id
            self.webtoons.append(webtoon_data)
            self.webtoon_id += 1

    def _exists(self, title: str) -> bool:
        return any(webtoon['title'] == title for webtoon in self.webtoons)

    def _update_day(self, webtoon_data: Dict[str, str]):
        for webtoon in self.webtoons:
            if webtoon['title'] == webtoon_data['title']:
                webtoon['day'] += ', ' + webtoon_data['day']
                break

    def save_to_json(self, filename: str):
        with open(f"{filename}.json", "w", encoding="utf-8") as output_file:
            json.dump(self.webtoons, output_file, ensure_ascii=False, indent=4)

class WebtoonCrawler:
    def __init__(self, scraper: WebtoonScraper, repository: WebtoonRepository):
        self.scraper = scraper
        self.repository = repository

    def run(self, urls: List[str]):
        for url in urls:
            self.scraper.open_page(url)
            webtoon_elements = self.scraper.get_webtoon_elements()

            for i, webtoon_element in enumerate(webtoon_elements):
                print(f"Processing: {i + 1} / {len(webtoon_elements)}")
                webtoon_data = self.scraper.scrape_webtoon_info(webtoon_element)
                if webtoon_data:
                    self.repository.save(webtoon_data)

def main():
    driver = WebDriverFactory.create_chrome_driver(CHROMEDRIVER_PATH)
    scraper = WebtoonScraper(driver)
    repository = WebtoonRepository()
    crawler = WebtoonCrawler(scraper, repository)

    try:
        crawler.run(NAVER_WEBTOON_URLS)
    finally:
        repository.save_to_json("webtoon_list")
        input("프로그램을 종료하려면 엔터를 누르세요...")
        driver.quit()

if __name__ == "__main__":
    main()
