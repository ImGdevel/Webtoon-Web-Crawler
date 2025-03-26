import os
import time
import json
from logger import Logger 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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

    def __init__(self, driver):
        self.driver = driver

    def get_thumbnail_url(self, soup):
        """웹툰 썸네일 URL을 추출하는 메서드"""
        try:
            img_tag = soup.find('div', {'class': self.THUMBNAIL_CLASS}).find('img')
            return img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else None
        except Exception:
            return None

    def fetch_webtoon(self, url: str):
        """웹툰 정보를 가져와 WebtoonDTO 객체로 반환"""
        try:
            logger.log("info", f"웹툰 페이지 접속: {url}")
            self.driver.get(url)
            time.sleep(2)  # 페이지 로딩 대기
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            thumbnail_url = self.get_thumbnail_url(soup)
            
            if thumbnail_url:
                logger.log("info", f"썸네일 URL: {thumbnail_url}")
                return WebtoonDTO(url, thumbnail_url)
            else:
                logger.log("warning", "썸네일을 찾을 수 없습니다.")
                return None
        except Exception as e:
            logger.log("error", f"크롤링 오류: {e}")
            return None

def save_to_json(webtoon_list, filename="webtoon_data.json"):
    """크롤링된 데이터를 JSON 파일로 저장"""
    data = [webtoon.to_dict() for webtoon in webtoon_list if webtoon]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.log("info", f"데이터 저장 완료: {filename}")

if __name__ == "__main__":
    driver_manager = ChromeWebDriverManager(headless=True)
    driver = driver_manager.get_driver()
    scraper = WebtoonScraper(driver)

    sample_urls = [
        "https://comic.naver.com/webtoon/list?titleId=747271",
        "https://comic.naver.com/webtoon/list?titleId=769209",
        "https://comic.naver.com/webtoon/list?titleId=776601",
    ]

    webtoon_list = [scraper.fetch_webtoon(url) for url in sample_urls]
    save_to_json(webtoon_list)

    driver.quit()
