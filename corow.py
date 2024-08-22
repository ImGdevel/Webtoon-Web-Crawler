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
from selenium.common.exceptions import StaleElementReferenceException

# 전역 상수로 HTML 클래스 이름을 설정하여 직관적인 변수명 사용
NAVER_WEBTOON_URL = 'https://comic.naver.com/webtoon/weekday'
CHROMEDRIVER_PATH = 'C:/chromedriver-win64/chromedriver.exe'
TITLE_AREA_CLASS = "ContentTitle__title_area--x24vt"
TITLE_CLASS = 'title'
DAY_TAB_CLASS = 'category_tab'
ON_DAY_CLASS = 'on'
THUMBNAIL_CLASS = 'thumb'
AUTHOR_CLASS = 'wrt_nm'
GENRE_CLASS = 'genre'
STORY_CLASS = 'detail'

# WebDriverFactory 클래스 - SRP 적용 (WebDriver 초기화와 관리 책임)
class WebDriverFactory:
    @staticmethod
    def create_chrome_driver(chromedriver_path: str) -> webdriver.Chrome:
        chrome_service = Service(chromedriver_path)
        chrome_options = Options()
        return webdriver.Chrome(service=chrome_service, options=chrome_options)

# WebtoonScraper 클래스의 scrape_webtoon_info 메서드를 수정합니다.
class WebtoonScraper:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def open_page(self, url: str):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

    def get_titles(self) -> List[webdriver.remote.webelement.WebElement]:
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, TITLE_AREA_CLASS))
        )

    def scrape_webtoon_info(self, title_element) -> Dict[str, str]:
        title_element.click()
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, TITLE_AREA_CLASS)))

            # 현재 URL이 로그인 페이지로 리디렉션되었는지 확인
            current_url = self.driver.current_url
            if "nidlogin.login" in current_url:
                print(f"Login required for this webtoon. Skipping: {current_url}")
                return None  # 웹툰 데이터를 수집하지 않음
            
            soup = bs(self.driver.page_source, 'html.parser')

            # 예외 처리하여 HTML 클래스 이름이 없는 경우 빈 문자열로 채움
            title = soup.find('span', {'class': TITLE_CLASS}).text.strip() if soup.find('span', {'class': TITLE_CLASS}) else ""
            day = soup.find('ul', {'class': DAY_TAB_CLASS}).find('li', {'class': ON_DAY_CLASS}).text.strip()[0:1] if soup.find('ul', {'class': DAY_TAB_CLASS}) else ""
            thumbnail_url = soup.find('div', {'class': THUMBNAIL_CLASS}).find('img')['src'] if soup.find('div', {'class': THUMBNAIL_CLASS}) else ""
            author = soup.find('span', {'class': AUTHOR_CLASS}).text.strip()[8:].replace(' / ', ', ') if soup.find('span', {'class': AUTHOR_CLASS}) else ""
            genre = soup.find('span', {'class': GENRE_CLASS}).text.strip() if soup.find('span', {'class': GENRE_CLASS}) else ""
            story = soup.find('div', {'class': STORY_CLASS}).find('p').text.strip() if soup.find('div', {'class': STORY_CLASS}) else ""
            
            return {
                "title": title,
                "day": day,
                "thumbnail_url": thumbnail_url,
                "author": author,
                "genre": genre,
                "story": story,
                "url": current_url
            }
        finally:
            self.driver.back()
            sleep(0.5)

# WebtoonRepository 클래스 - SRP 적용 (데이터 저장과 관리 책임)
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

    def save_to_csv(self, filename: str):
        keys = ["id", "title", "day", "thumbnail_url", "author", "genre", "story", "url"]
        with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.webtoons)

# WebtoonCrawler 클래스의 run 메서드를 수정합니다.
class WebtoonCrawler:
    def __init__(self, scraper: WebtoonScraper, repository: WebtoonRepository):
        self.scraper = scraper
        self.repository = repository

    def run(self, url: str):
        self.scraper.open_page(url)
        titles = self.scraper.get_titles()

        for i in range(len(titles)):
            print(f"Process: {i + 1} / {len(titles)}", end="\r")
            try:
                # 새로운 title_elements를 매번 가져옵니다.
                titles = self.scraper.get_titles()  
                title_element = titles[i]

                # 클릭 전에 stale 상태인지 확인하고 재시도합니다.
                webtoon_data = self._retry_click_and_scrape(title_element)
                if webtoon_data:
                    self.repository.save(webtoon_data)

            except StaleElementReferenceException:
                print(f"StaleElementReferenceException: Element is stale at index {i}. Retrying...")
                continue

    def _retry_click_and_scrape(self, title_element, retries=3):
        for _ in range(retries):
            try:
                return self.scraper.scrape_webtoon_info(title_element)
            except StaleElementReferenceException:
                sleep(0.5)
        raise StaleElementReferenceException("Element is stale after multiple retries.")

# main 함수 - OCP 적용 (비즈니스 로직 분리)
def main():
    driver = WebDriverFactory.create_chrome_driver(CHROMEDRIVER_PATH)
    scraper = WebtoonScraper(driver)
    repository = WebtoonRepository()
    crawler = WebtoonCrawler(scraper, repository)

    try:
        crawler.run(NAVER_WEBTOON_URL)
    finally:
        repository.save_to_csv("webtoon_list")
        driver.quit()

if __name__ == "__main__":
    main()
