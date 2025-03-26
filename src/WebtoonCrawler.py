import os
import time
import json
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
    def __init__(self, url: str, thumbnail_url: str):
        self.url = url
        self.thumbnail_url = thumbnail_url

    def to_dict(self):
        return {"url": self.url, "thumbnail": self.thumbnail_url}

class WebtoonScraper:
    """웹툰 정보를 크롤링하는 클래스"""

    THUMBNAIL_CLASS = 'Poster__thumbnail_area--gviWY'
    WAITING_LOAD_PAGE = 5  # 최대 대기 시간 (초)

    def __init__(self, driver):
        self.driver = driver

    def get_thumbnail_url(self):
        """웹툰 썸네일 URL을 추출하는 메서드"""
        try:
            img_element = WebDriverWait(self.driver, self.WAITING_LOAD_PAGE).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.THUMBNAIL_CLASS))
            )
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            img_tag = soup.find('div', {'class': self.THUMBNAIL_CLASS}).find('img')
            return img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else None
        except Exception:
            return None

    def fetch_webtoon(self, url: str):
        """웹툰 정보를 가져와 WebtoonDTO 객체로 반환"""
        try:
            logger.log("info", f"웹툰 페이지 접속: {url}")
            self.driver.get(url)
            
            thumbnail_url = self.get_thumbnail_url()
            
            if thumbnail_url:
                logger.log("info", f"썸네일 URL: {thumbnail_url}")
                return True, WebtoonDTO(url, thumbnail_url)
            else:
                logger.log("warning", "썸네일을 찾을 수 없습니다.")
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
