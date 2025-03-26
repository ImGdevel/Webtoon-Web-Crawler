import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


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
        except Exception as e:
            print(f"❌ 크롬 드라이버 설치 오류: {e}")
            return

    def get_driver(self):
        """설정된 크롬 드라이버를 반환하는 메서드"""
        if not self.driver_path:
            print("🚨 크롬 드라이버를 찾을 수 없습니다. 다시 설정합니다.")
            self.setup_driver()

        options = Options()
        if self.headless:
            options.add_argument("--headless")

        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver


class WebtoonCrawler:
    """웹툰 리스트 페이지를 크롤링하는 클래스"""

    THUMBNAIL_CLASS = 'Poster__thumbnail_area--gviWY'

    def __init__(self, driver_manager: ChromeWebDriverManager):
        self.driver_manager = driver_manager
        self.driver = driver_manager.get_driver()
        self.data = []

    def get_thumbnail_url(self, soup):
        """웹툰 썸네일 URL을 추출하는 메서드"""
        try:
            img_tag = soup.find('div', {'class': self.THUMBNAIL_CLASS}).find('img')
            return img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else None
        except Exception:
            return None

    def fetch_webtoon_list(self, url: str):
        """웹툰 리스트 페이지에서 데이터를 가져옴"""
        try:
            print(f"🌍 웹툰 페이지 접속: {url}")
            self.driver.get(url)
            time.sleep(2)  # 페이지 로딩 대기
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            thumbnail_url = self.get_thumbnail_url(soup)
            
            if thumbnail_url:
                print(f"🖼️ 썸네일 URL: {thumbnail_url}")
                self.data.append({"url": url, "thumbnail": thumbnail_url})
            else:
                print("🚨 썸네일을 찾을 수 없습니다.")
        except Exception as e:
            print(f"🚨 크롤링 오류: {e}")

    def save_to_json(self, filename="webtoon_data.json"):
        """크롤링된 데이터를 JSON 파일로 저장"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        print(f"💾 데이터 저장 완료: {filename}")

    def close(self):
        """드라이버 종료"""
        self.driver.quit()


# 📌 실행 예제
if __name__ == "__main__":
    driver_manager = ChromeWebDriverManager(headless=True)
    crawler = WebtoonCrawler(driver_manager)

    sample_urls = [
        "https://comic.naver.com/webtoon/list?titleId=747271",
        "https://comic.naver.com/webtoon/list?titleId=769209",
        "https://comic.naver.com/webtoon/list?titleId=776601",
    ]

    for url in sample_urls:
        crawler.fetch_webtoon_list(url)

    crawler.save_to_json()
    crawler.close()