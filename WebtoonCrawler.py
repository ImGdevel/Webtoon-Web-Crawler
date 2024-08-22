from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from bs4 import BeautifulSoup as bs
from time import sleep
import re
import json

# WebDriverFactory를 인터페이스로 정의하여 확장성을 높임
class WebDriverFactory(ABC):
    @abstractmethod
    def create_driver(self) -> webdriver.Chrome:
        pass

class ChromeWebDriverFactory(WebDriverFactory):
    def __init__(self, chromedriver_path: str):
        self.chromedriver_path = chromedriver_path

    def create_driver(self) -> webdriver.Chrome:
        chrome_service = Service(self.chromedriver_path)
        chrome_options = Options()
        return webdriver.Chrome(service=chrome_service, options=chrome_options)

# WebtoonScraper 인터페이스 정의
class WebtoonScraper(ABC):
    @abstractmethod
    def get_urls(self) -> list:
        pass

    @abstractmethod
    def open_page(self, url: str):
        pass

    @abstractmethod
    def get_webtoon_elements(self) -> list:
        pass

    @abstractmethod
    def scrape_webtoon_info(self, webtoon_element) -> dict:
        pass

# NaverWebtoonScraper 구현
class NaverWebtoonScraper(WebtoonScraper):
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
    CONTENT_LIST_CLASS = "ContentList__content_list--q5KXY"
    ITEM_CLASS = "item"
    RATING_CLASS = "Rating__star_area--dFzsb"
    TITLE_AREA_CLASS = "ContentTitle__title_area--x24vt"

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def get_urls(self) -> list:
        return self.NAVER_WEBTOON_URLS

    def open_page(self, url: str):
        self.driver.get(url)
        WebDriverWait(self.driver, 3).until(lambda d: d.execute_script('return document.readyState') == 'complete')

    def get_webtoon_elements(self) -> list:
        return WebDriverWait(self.driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, self.ITEM_CLASS))
        )

    def scrape_webtoon_info(self, webtoon_element) -> dict:
        try:
            rating = WebDriverWait(webtoon_element, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.RATING_CLASS))
            ).text.strip()

            title_element = webtoon_element.find_element(By.CLASS_NAME, self.TITLE_AREA_CLASS)
            title_element.click()

            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, self.TITLE_AREA_CLASS)))
            soup = bs(self.driver.page_source, 'html.parser')

            title = soup.find('h2', {'class': 'EpisodeListInfo__title--mYLjC'}).text.strip()
            day_age = soup.find('div', {'class': 'ContentMetaInfo__meta_info--GbTg4'}).find('em', {'class': 'ContentMetaInfo__info_item--utGrf'}).text.strip()
            thumbnail_url = soup.find('div', {'class': 'Poster__thumbnail_area--gviWY'}).find('img')['src']
            story = soup.find('div', {'class': 'EpisodeListInfo__summary_wrap--ZWNW5'}).find('p').text.strip()

            rating = re.search(r'\d+\.\d+', rating).group(0)
            day_match = re.search(r'(월|화|수|목|금|토|일)|완결', day_age)
            day = day_match.group(0) if day_match else None

            age_rating_match = re.search(r'(전체연령가|\d+세)', day_age)
            age_rating = age_rating_match.group(0) if age_rating_match else None

            return {
                "title": title,
                "day": day,
                "rating": rating,
                "thumbnail_url": thumbnail_url,
                "story": story,
                "url": self.driver.current_url,
                "age_rating": age_rating
            }
        except TimeoutException:
            print("TimeoutException: Could not load webtoon page. Skipping...")
            return None
        finally:
            self.driver.back()
            sleep(0.5)

# KaKaoWebtoonScraper 구현
class KaKaoWebtoonScraper(WebtoonScraper):
    KAKAO_WEBTOON_URLS = [
        'https://webtoon.kakao.com/original'
    ]
    # 이 부분에 다른 필요한 상수들을 추가하세요

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def get_urls(self) -> list:
        return self.KAKAO_WEBTOON_URLS

    def open_page(self, url: str):
        self.driver.get(url)
        WebDriverWait(self.driver, 3).until(lambda d: d.execute_script('return document.readyState') == 'complete')

    def get_webtoon_elements(self) -> list:
        # KaKao 웹툰 사이트의 웹툰 엘리먼트를 찾는 로직 구현
        pass

    def scrape_webtoon_info(self, webtoon_element) -> dict:
        # KaKao 웹툰 정보를 스크래핑하는 로직 구현
        pass

# Repository 인터페이스 정의
class WebtoonRepository(ABC):
    @abstractmethod
    def save(self, webtoon_data: dict):
        pass

    @abstractmethod
    def save_to_json(self, filename: str):
        pass

class JsonWebtoonRepository(WebtoonRepository):
    def __init__(self):
        self.webtoons = []
        self.webtoon_id = 0

    def save(self, webtoon_data: dict):
        if self._exists(webtoon_data["title"]):
            self._update_day(webtoon_data)
        else:
            webtoon_data["id"] = self.webtoon_id
            self.webtoons.append(webtoon_data)
            self.webtoon_id += 1

    def _exists(self, title: str) -> bool:
        return any(webtoon['title'] == title for webtoon in self.webtoons)

    def _update_day(self, webtoon_data: dict):
        for webtoon in self.webtoons:
            if webtoon['title'] == webtoon_data['title']:
                webtoon['day'] += ', ' + webtoon_data['day']
                break

    def save_to_json(self, filename: str):
        with open(f"{filename}.json", "w", encoding="utf-8") as output_file:
            json.dump(self.webtoons, output_file, ensure_ascii=False, indent=4)

# Crawler 클래스는 웹스크래퍼와 레포지토리에 의존
class WebtoonCrawler:
    def __init__(self, scraper: WebtoonScraper, repository: WebtoonRepository):
        self.scraper = scraper
        self.repository = repository

    def run(self):
        for url in self.scraper.get_urls():
            self.scraper.open_page(url)
            webtoon_elements = self.scraper.get_webtoon_elements()
            webtoon_list_len = 2 #len(webtoon_elements)
            for i in range(webtoon_list_len):
                try:
                    print(f"Processing: {i + 1} / {webtoon_list_len}")

                    webtoon_elements = self.scraper.get_webtoon_elements()
                    webtoon_data = self.scraper.scrape_webtoon_info(webtoon_elements[i])

                    if webtoon_data:
                        self.repository.save(webtoon_data)
                except StaleElementReferenceException:
                    print(f"StaleElementReferenceException encountered on element {i + 1}. Retrying...")
                    continue

# Factory Method를 사용하는 메인 함수
def main():
    driver_factory = ChromeWebDriverFactory('C:/chromedriver-win64/chromedriver.exe')
    driver = driver_factory.create_driver()
    repository = JsonWebtoonRepository()

    scraper_type = 'naver'  # 'kakao'를 입력하면 KaKaoWebtoonScraper를 사용할 수 있습니다.

    if scraper_type == 'naver':
        scraper = NaverWebtoonScraper(driver)
    elif scraper_type == 'kakao':
        scraper = KaKaoWebtoonScraper(driver)

    crawler = WebtoonCrawler(scraper, repository)

    try:
        crawler.run()
    finally:
        repository.save_to_json("webtoon_list")
        input("프로그램을 종료하려면 엔터를 누르세요...")
        driver.quit()

if __name__ == "__main__":
    main()
