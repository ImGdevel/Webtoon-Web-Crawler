import os
import time
import json
import re
from logger import Logger 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logger = Logger()

class ChromeWebDriverManager:
    """크롬 드라이버를 자동으로 관리하는 클래스"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver_path = None
        self.setup_driver()

    def setup_driver(self):
        """드라이버를 자동으로 다운로드하고 설정하는 메서드"""
        try:
            self.driver_path = ChromeDriverManager().install()
            logger.log("info", "크롬 드라이버 설치 완료")
        except Exception as e:
            logger.log("error", f"크롬 드라이버 설치 오류: {e}")

    def get_driver(self):
        """설정된 크롬 드라이버를 반환하는 메서드"""
        if not self.driver_path:
            logger.log("warning", "크롬 드라이버를 찾을 수 없습니다. 다시 설정합니다.")
            self.setup_driver()

        options = Options()
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920x1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        logger.log("info", "크롬 드라이버 실행 완료")
        return driver

class WebtoonDTO:
    """웹툰 정보를 저장하는 데이터 객체"""
    def __init__(self, url, title, external_id, platform, day_of_week, thumbnail_url, link, age_rating, description, serialization_status, episode_count):
        self.url = url
        self.title = title
        self.external_id = external_id
        self.platform = platform
        self.day_of_week = day_of_week
        self.thumbnail_url = thumbnail_url
        self.link = link
        self.age_rating = age_rating
        self.description = description
        self.serialization_status = serialization_status
        self.episode_count = episode_count

    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "externalId": self.external_id,
            "platform": self.platform,
            "dayOfWeek": self.day_of_week,
            "thumbnailUrl": self.thumbnail_url,
            "link": self.link,
            "ageRating": self.age_rating,
            "description": self.description,
            "serializationStatus": self.serialization_status,
            "episodeCount": self.episode_count
        }

class WebtoonScraper:
    """웹툰 정보를 크롤링하는 클래스"""

    TITLE_CLASS = "EpisodeListInfo__title--mYLjC"
    THUMBNAIL_CLASS = "Poster__thumbnail_area--gviWY"
    SUMMARY_CLASS = "EpisodeListInfo__summary_wrap--ZWNW5"
    EPISODE_COUNT_CLASS = "EpisodeListView__count--fTMc5"
    WAITING_LOAD_PAGE = 5  # 최대 대기 시간 (초)

    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, class_name):
        return WebDriverWait(self.driver, self.WAITING_LOAD_PAGE).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )

    def get_title(self):
        element = self.wait_for_element(self.TITLE_CLASS)
        return element.text.strip()

    def get_thumbnail_url(self):
        element = self.wait_for_element(self.THUMBNAIL_CLASS)
        return element.find_element(By.TAG_NAME, 'img').get_attribute('src')

    def get_story(self):
        element = self.wait_for_element(self.SUMMARY_CLASS)
        return element.find_element(By.TAG_NAME, 'p').text.strip()

    def get_unique_id(self, url):
        id_match = re.search(r'titleId=(\d+)', url)
        return int(id_match.group(1)) if id_match else None

    def get_episode_count(self):
        element = self.wait_for_element(self.EPISODE_COUNT_CLASS)
        return int(re.search(r'\d+', element.text).group()) if element else None

    def fetch_webtoon(self, url):
        """웹툰 정보를 가져와 WebtoonDTO 객체로 반환"""
        try:
            logger.log("info", f"웹툰 페이지 접속: {url}")
            self.driver.get(url)
            
            title = self.get_title()
            external_id = self.get_unique_id(url)
            thumbnail_url = self.get_thumbnail_url()
            description = self.get_story()
            episode_count = self.get_episode_count()
            
            if title and external_id and thumbnail_url:
                webtoon_data = WebtoonDTO(url, title, external_id, "Naver", None, thumbnail_url, url, None, description, None, episode_count)
                return True, webtoon_data
            else:
                logger.log("warning", "필수 정보를 찾을 수 없습니다.")
                return False, None
        except Exception as e:
            logger.log("error", f"크롤링 오류: {e}")
            return False, None

class WebtoonCrawler:
    """웹툰 크롤러 클래스"""

    def __init__(self, urls):
        self.urls = urls
        self.driver_manager = ChromeWebDriverManager(headless=True)
        self.driver = self.driver_manager.get_driver()
        self.scraper = WebtoonScraper(self.driver)
        self.success_list = []
        self.failure_list = []

    def run(self):
        """크롤링 실행 메서드"""
        for url in self.urls:
            success, webtoon_data = self.scraper.fetch_webtoon(url)
            if success:
                self.success_list.append(webtoon_data.to_dict())
            else:
                self.failure_list.append({"url": url})

        self.save_results()
        self.driver.quit()

    def save_results(self):
        """크롤링 결과를 JSON 파일로 저장"""
        save_to_json(self.success_list, "webtoon_data.json")
        save_to_json(self.failure_list, "failed_webtoon_list.json")

def save_to_json(data_list, filename):
    """크롤링된 데이터를 JSON 파일로 저장"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_list, f, indent=4, ensure_ascii=False)
    logger.log("info", f"데이터 저장 완료: {filename}")

if __name__ == "__main__":
    sample_urls = [
        "https://comic.naver.com/webtoon/list?titleId=747271",
        "https://comic.naver.com/webtoon/list?titleId=769209",
        "https://comic.naver.com/webtoon/list?titleId=776601",
    ]
    crawler = WebtoonCrawler(sample_urls)
    crawler.run()
